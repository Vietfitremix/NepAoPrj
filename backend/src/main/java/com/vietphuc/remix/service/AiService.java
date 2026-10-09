package com.vietphuc.remix.service;
import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.databind.json.JsonMapper;
import com.vietphuc.remix.client.AiClient;
import com.vietphuc.remix.dto.request.*;
import com.vietphuc.remix.dto.response.*;
import com.vietphuc.remix.dto.response.AiDtos.*;
import com.vietphuc.remix.exception.ApiException;
import jakarta.validation.Validator;
import org.springframework.stereotype.Service;
import java.util.*;
@Service
public class AiService {
    private final AiClient client;
    private final OutfitService outfits;
    private final SelectionService selections;
    private final Validator validator;
    private final ObjectMapper mapper;
    public AiService(AiClient client,OutfitService outfits,SelectionService selections,Validator validator,ObjectMapper mapper) {
        this.client=client; this.outfits=outfits; this.selections=selections; this.validator=validator;
        this.mapper=JsonMapper.builder()
                .disable(MapperFeature.ALLOW_COERCION_OF_SCALARS)
                .enable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)
                .enable(DeserializationFeature.FAIL_ON_NULL_FOR_PRIMITIVES)
                .disable(DeserializationFeature.ACCEPT_FLOAT_AS_INT).build();
    }
    public List<Concept> recommend(RecommendationRequest request,WeatherResponse weather) {
        var payload=new LinkedHashMap<String,Object>();
        payload.put("prompt",request.prompt()); payload.put("city",request.city());
        payload.put("eventCode",request.eventCode()); payload.put("styleCode",request.styleCode());
        payload.put("character",request.character());
        payload.put("weather",weather); payload.put("referenceData",outfits.references());
        payload.put("culturalContext",outfits.culturalContext());
        var data=client.recommendations(payload);
        if(data==null || !data.isObject() || !data.path("concepts").isArray() || data.path("concepts").size()!=3)
            throw invalidOutput();
        List<Concept> result=new ArrayList<>();
        for(JsonNode node:data.path("concepts")) {
            var concept=convert(node,Concept.class);
            validateAiSelection(new LookSelection(concept.outfitCode(),concept.colorCode(),concept.styleCode(),
                    request.eventCode(),concept.accessories()));
            result.add(concept);
        }
        return List.copyOf(result);
    }
    public RemixResponse remix(RemixRequest request) {
        selections.validate(request.currentLook());
        var payload=new LinkedHashMap<String,Object>();
        payload.put("prompt",request.prompt()); payload.put("currentLook",request.currentLook());
        payload.put("referenceData",outfits.references()); payload.put("culturalContext",outfits.culturalContext());
        var response=convert(client.remix(payload),RemixResponse.class);
        var change=response.changes();
        var removed=new HashSet<>(change.removeAccessories());
        var added=new HashSet<>(change.addAccessories());
        var selected=new LinkedHashSet<>(request.currentLook().accessories());
        if(removed.size()!=change.removeAccessories().size() || added.size()!=change.addAccessories().size() ||
            !selected.containsAll(removed) || !Collections.disjoint(removed,added) ||
            !Collections.disjoint(selected,added)) throw invalidOutput();
        selected.removeAll(removed); selected.addAll(added);
        var current=request.currentLook();
        validateAiSelection(new LookSelection(current.outfitCode(),
            change.colorCode()==null?current.colorCode():change.colorCode(),
            change.styleCode()==null?current.styleCode():change.styleCode(),
            current.eventCode(),List.copyOf(selected)));
        return response;
    }
    private <T> T convert(JsonNode node,Class<T> type) {
        try {
            var value=mapper.treeToValue(node,type);
            if(value==null || !validator.validate(value).isEmpty()) throw invalidOutput();
            return value;
        } catch(com.fasterxml.jackson.core.JsonProcessingException | IllegalArgumentException e) {
            throw invalidOutput();
        }
    }
    private void validateAiSelection(LookSelection look) {
        try {
            if(!validator.validate(look).isEmpty()) throw invalidOutput();
            selections.validate(look);
        } catch(ApiException e) { throw invalidOutput(); }
    }
    private ApiException invalidOutput() {
        return new ApiException(org.springframework.http.HttpStatus.BAD_GATEWAY,"INVALID_AI_OUTPUT",
            "AI trả dữ liệu sai định dạng, số concept hoặc mã không được hỗ trợ.");
    }
}
