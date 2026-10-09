package com.vietphuc.remix;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;
import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.hamcrest.Matchers.hasSize;

@SpringBootTest @AutoConfigureMockMvc @ActiveProfiles("test") @Transactional
class DataCatalogIntegrationTest {
    @Autowired MockMvc mvc;
    @Autowired JdbcTemplate jdbc;

    @Test void fullWardrobesAndEightQuestionsComeFromDatabase() throws Exception {
        mvc.perform(get("/api/data/bootstrap")).andExpect(status().isOk())
            .andExpect(jsonPath("$.wardrobes.male.outfits",hasSize(5)))
            .andExpect(jsonPath("$.wardrobes.female.outfits",hasSize(6)))
            .andExpect(jsonPath("$.wardrobes.male.accessories",hasSize(16)))
            .andExpect(jsonPath("$.wardrobes.female.accessories",hasSize(21)))
            .andExpect(jsonPath("$.wardrobes.male.shoes",hasSize(8)))
            .andExpect(jsonPath("$.wardrobes.female.shoes",hasSize(8)))
            .andExpect(jsonPath("$.quiz",hasSize(8)))
            .andExpect(jsonPath("$.quiz[7].options",hasSize(9)));
        mvc.perform(get("/api/data/documents/ai.scoring")).andExpect(status().isOk())
            .andExpect(jsonPath("$.criteria",hasSize(5)));
        mvc.perform(get("/api/data/documents/ai.rules")).andExpect(status().isOk())
            .andExpect(jsonPath("$",hasSize(34)));
    }
    @Test void mergedAiRulesScoringAndPromptsAreAvailableFromDatabase() throws Exception {
        var mapper=new com.fasterxml.jackson.databind.ObjectMapper();
        var rules=mapper.readTree(mvc.perform(get("/api/data/documents/ai.rules"))
            .andExpect(status().isOk()).andReturn().getResponse().getContentAsString(StandardCharsets.UTF_8));
        for(var rule:rules) {
            String metadata=jdbc.queryForObject("SELECT metadata::text FROM ai_cultural_rules WHERE rule_key=? AND active=TRUE",String.class,rule.path("id").asText());
            assertEquals(rule,parseStoredJson(metadata),rule.path("id").asText());
        }
        for(var entry:java.util.Map.of("R40",35,"R41",35,"R42",40,"R45",45).entrySet()) {
            var rule=parseStoredJson(jdbc.queryForObject("SELECT metadata::text FROM ai_cultural_rules WHERE rule_key=?",String.class,entry.getKey()));
            assertEquals(entry.getValue().intValue(),rule.path("cap").asInt());
            assertFalse(rule.path("verified").asBoolean());
            assertFalse(rule.path("sourceNote").asText().isBlank());
        }
        var existing=parseStoredJson(jdbc.queryForObject("SELECT metadata::text FROM ai_cultural_rules WHERE rule_key='R01'",String.class));
        assertTrue(existing.path("sources").get(0).asText().startsWith("https://dsvh.gov.vn/"));
        mvc.perform(get("/api/data/documents/ai.scoring")).andExpect(status().isOk())
            .andExpect(jsonPath("$.rankBonus.preferredColor").value(20));
        String select=parseStoredJson(jdbc.queryForObject("SELECT payload::text FROM data_documents WHERE data_key='prompt.select'",String.class)).path("template").asText();
        String review=parseStoredJson(jdbc.queryForObject("SELECT payload::text FROM data_documents WHERE data_key='prompt.review'",String.class)).path("template").asText();
        assertTrue(select.contains("3 KIỂU ÁO KHÁC NHAU"));
        assertTrue(review.contains("KHÔNG khen vòng vo"));
    }
    private com.fasterxml.jackson.databind.JsonNode parseStoredJson(String raw) throws Exception {
        var mapper=new com.fasterxml.jackson.databind.ObjectMapper();
        var value=mapper.readTree(raw);
        // H2's PostgreSQL mode returns a JSON string around the stored document.
        return value.isTextual()?mapper.readTree(value.asText()):value;
    }
    @Test void genderSpecificItemsAreFilteredAndSharedItemsRemainAvailable() throws Exception {
        var json=new com.fasterxml.jackson.databind.ObjectMapper().readTree(
            mvc.perform(get("/api/data/bootstrap")).andReturn().getResponse().getContentAsString(StandardCharsets.UTF_8));
        for(String character:List.of("male","female")) {
            for(String category:List.of("outfits","pants","shoes","accessories")) {
                for(var item:json.path("wardrobes").path(character).path(category))
                    assertTrue(List.of("unisex",character).contains(item.path("gender").asText()),character+"/"+item.path("id"));
            }
            var accessories=json.path("wardrobes").path(character).path("accessories");
            assertTrue(java.util.stream.StreamSupport.stream(accessories.spliterator(),false)
                .anyMatch(item->item.path("id").asText().equals("tai-nghe")));
        }
        // Filtering does not delete the source items or their metadata.
        assertEquals(86L,jdbc.queryForObject("SELECT COUNT(*) FROM wardrobe_items",Long.class));
    }
    @Test void everyNewCatalogTableHasItsSeedData() {
        for(String table:List.of("data_documents","wardrobe_items","ai_catalog_entries","ai_cultural_rules",
            "quiz_questions","scoring_criteria","checklist_entries"))
            assertTrue(jdbc.queryForObject("SELECT COUNT(*) FROM "+table,Long.class)>0,table);
        assertEquals(86L,jdbc.queryForObject("SELECT COUNT(*) FROM wardrobe_items",Long.class));
        // A fresh migration contains 62 rules; existing user databases can have additional rules.
        assertEquals(62L,jdbc.queryForObject("SELECT COUNT(*) FROM cultural_rules",Long.class));
        assertEquals(0L,jdbc.queryForObject("SELECT COUNT(*) FROM outfit_assets WHERE image_url LIKE '%.svg'",Long.class));
    }
    @Test void assetBytesRoundTripFromDatabaseWithConditionalCacheAndManifest() throws Exception {
        byte[] bytes="Exact unchanged asset bytes".getBytes(StandardCharsets.UTF_8);
        String sha=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
        String path="frontend/public/figure/database-test.png";
        jdbc.update("INSERT INTO asset_files(relative_path,content_type,byte_size,sha256,file_data) VALUES (?,?,?,?,?)",
            path,"image/png",bytes.length,sha,bytes);
        mvc.perform(get("/figure/database-test.png")).andExpect(status().isOk())
            .andExpect(content().bytes(bytes)).andExpect(content().contentType("image/png"))
            .andExpect(header().string("ETag","\""+sha+"\""));
        mvc.perform(get("/figure/database-test.png").header("If-None-Match","\""+sha+"\""))
            .andExpect(status().isNotModified());
        mvc.perform(get("/api/assets/"+path)).andExpect(status().isOk()).andExpect(content().bytes(bytes));
        mvc.perform(get("/api/data/assets").param("prefix","frontend/public/figure/database-test"))
            .andExpect(status().isOk()).andExpect(jsonPath("$",hasSize(1)))
            .andExpect(jsonPath("$[0].sha256").value(sha));
    }
    @Test void unknownAssetsAndDocumentsAreNotFound() throws Exception {
        mvc.perform(get("/figure/does-not-exist.png")).andExpect(status().isNotFound());
        mvc.perform(get("/api/data/documents/unknown")).andExpect(status().isNotFound());
    }
    @Test void culturalSourcesAreScopedAndOriginalProvenanceIsKept() throws Exception {
        mvc.perform(get("/api/data/documents/cultural.sources")).andExpect(status().isOk())
            .andExpect(jsonPath("$",hasSize(10)))
            .andExpect(jsonPath("$[0].httpStatus").value(200));
        assertEquals(15L,jdbc.queryForObject("SELECT COUNT(*) FROM cultural_knowledge WHERE source_url LIKE 'https://%' AND original_content IS NOT NULL",Long.class));
        assertEquals(0L,jdbc.queryForObject("SELECT COUNT(*) FROM cultural_rules WHERE source_url NOT LIKE 'https://%' OR source_note IS NULL OR original_source_url IS NULL",Long.class));
        // A working article URL alone does not verify an application's styling recommendation.
        assertEquals(0L,jdbc.queryForObject("SELECT COUNT(*) FROM cultural_rules WHERE source_verified=TRUE",Long.class));
        mvc.perform(post("/api/cultural-score").contentType("application/json").content("""
            {"outfitCode":"NHAT_BINH","colorCode":"RED","styleCode":"GEN_Z","eventCode":"PHOTOSHOOT","accessories":["NON_LA"]}
            """))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.warnings[0].sourceUrl").value(org.hamcrest.Matchers.startsWith("https://khamphahue.com.vn/")))
            .andExpect(jsonPath("$.warnings[0].sourceVerified").value(false))
            .andExpect(jsonPath("$.warnings[0].sourceNote").isNotEmpty());
    }
    @Test void everyGarmentHasDetailedCultureWithSectionSpecificSources() throws Exception {
        for(String code:List.of("AO_DAI","AO_TU_THAN","AO_NGU_THAN","NHAT_BINH","AO_BA_BA")) {
            mvc.perform(get("/api/outfits/"+code+"/cultural-knowledge")).andExpect(status().isOk())
                .andExpect(jsonPath("$",hasSize(6)));
            List<String> categories=jdbc.queryForList("SELECT k.category FROM cultural_knowledge k JOIN outfits o ON o.id=k.outfit_id WHERE o.code=?",String.class,code);
            assertEquals(java.util.Set.of("ORIGIN","CHARACTERISTICS","MEANING","WEARING","CONTEXT","PRESERVATION"),new java.util.HashSet<>(categories));
            List<String> contents=jdbc.queryForList("SELECT k.content FROM cultural_knowledge k JOIN outfits o ON o.id=k.outfit_id WHERE o.code=?",String.class,code);
            assertTrue(contents.stream().mapToInt(text->text.split("\\s+").length).sum()>=300,code);
        }
        assertEquals(0L,jdbc.queryForObject("SELECT COUNT(*) FROM cultural_knowledge WHERE content IS NULL OR LENGTH(TRIM(content))<100 OR source_name IS NULL OR source_url NOT LIKE 'https://%'",Long.class));
    }
}
