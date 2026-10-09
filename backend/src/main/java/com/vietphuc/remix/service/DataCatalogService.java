package com.vietphuc.remix.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.vietphuc.remix.exception.ApiException;
import java.util.*;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service @RequiredArgsConstructor @Transactional(readOnly=true)
public class DataCatalogService {
    private final JdbcTemplate jdbc;
    private final ObjectMapper mapper;

    public JsonNode parse(String json) {
        try {
            JsonNode value=mapper.readTree(json);
            return value.isTextual()?mapper.readTree(value.textValue()):value;
        } catch (java.io.IOException e) { throw new IllegalStateException("Stored catalog JSON is invalid",e); }
    }
    public JsonNode document(String key) {
        var rows=jdbc.queryForList("SELECT payload::text FROM data_documents WHERE data_key=?",String.class,key);
        if(rows.isEmpty())throw ApiException.notFound("Không tìm thấy dữ liệu: "+key);
        return parse(rows.getFirst());
    }
    public ObjectNode bootstrap() {
        ObjectNode result=mapper.createObjectNode();
        ObjectNode wardrobes=result.putObject("wardrobes");
        for(String character:List.of("male","female")) {
            ObjectNode catalog=(ObjectNode)document("wardrobe."+character).deepCopy();
            for(String category:List.of("outfits","pants","shoes","accessories")) {
                Map<String,JsonNode> items=new LinkedHashMap<>();
                jdbc.query("SELECT item_key,metadata::text,gender_scope FROM wardrobe_items WHERE character=? AND category=? AND (gender_scope='unisex' OR gender_scope=?) ORDER BY item_key",
                    rs->{items.put(rs.getString(1),((ObjectNode)parse(rs.getString(2))).put("gender",rs.getString(3)));},character,category,character);
                ArrayNode ordered=mapper.createArrayNode();
                for(JsonNode original:catalog.path(category)) {
                    JsonNode item=items.remove(original.path("id").asText());
                    if(item!=null)ordered.add(item);
                }
                items.values().forEach(ordered::add);
                catalog.set(category,ordered);
            }
            wardrobes.set(character,catalog);
        }
        JsonNode colors=document("wardrobe.colors");
        result.set("colors",colors);
        result.set("patterns",document("wardrobe.patterns"));
        ArrayNode quiz=result.putArray("quiz");
        for(String json:jdbc.queryForList("SELECT metadata::text FROM quiz_questions ORDER BY sort_order",String.class)) {
            ObjectNode question=(ObjectNode)parse(json);
            if(question.path("options").isTextual() && question.path("options").asText().equals("palette")) {
                ArrayNode options=question.putArray("options");
                for(JsonNode color:colors)options.addObject().put("value",color.path("value").asText())
                    .put("label",color.path("name").asText()).put("hex",color.path("value").asText());
            }
            quiz.add(question);
        }
        result.put("assetCount",jdbc.queryForObject("SELECT COUNT(*) FROM asset_files",Long.class));
        return result;
    }
    public List<Map<String,Object>> assetManifest(String prefix) {
        // startsWith semantics; a user-supplied % or _ must not become a SQL wildcard.
        String escaped=prefix.replace("!","!!").replace("%","!%").replace("_","!_");
        return jdbc.queryForList("SELECT relative_path,content_type,byte_size,sha256 FROM asset_files WHERE relative_path LIKE ? ESCAPE '!' ORDER BY relative_path",escaped+"%");
    }
}
