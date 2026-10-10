package com.vietphuc.remix;
import com.fasterxml.jackson.databind.*;
import com.vietphuc.remix.client.*;
import com.vietphuc.remix.dto.response.WeatherResponse;
import com.vietphuc.remix.entity.*;
import com.vietphuc.remix.enums.*;
import com.vietphuc.remix.repository.*;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;
import java.util.*;
import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
@SpringBootTest @AutoConfigureMockMvc @ActiveProfiles("test") @Transactional
class ApiIntegrationTest {
    @Autowired MockMvc mvc;
    @Autowired ObjectMapper mapper;
    @Autowired CulturalRuleRepository rules;
    @Autowired OutfitRepository outfits;
    @Autowired LookRepository looks;
    @Autowired OutfitAccessoryRepository supported;
    @MockBean WeatherClient weather;
    @MockBean AiClient ai;
    private static final String SELECTION="""
        {"outfitCode":"AO_DAI","colorCode":"RED","styleCode":"GEN_Z","eventCode":"FESTIVAL","accessories":["NON_LA"]}
        """;
    private static final String RECOMMEND="""
        {"prompt":"Đi lễ hội, muốn phong cách trẻ trung","city":"Hanoi","eventCode":"FESTIVAL","styleCode":"GEN_Z"}
        """;
    @BeforeEach void setUp() {
        when(weather.current("Hanoi")).thenReturn(new WeatherResponse("Hanoi",31.5,"CLEAR",70));
        rules.deleteAll();
    }
    private JsonNode concepts() throws Exception {
        return mapper.readTree("""
            {"concepts":[
                {"conceptName":"A","outfitCode":"AO_DAI","colorCode":"RED","styleCode":"GEN_Z","accessories":["NON_LA"],"matchScore":92,"reason":"Phù hợp yêu cầu"},
                {"conceptName":"B","outfitCode":"AO_TU_THAN","colorCode":"BLUE","styleCode":"MINIMAL","accessories":[],"matchScore":85,"reason":"Phù hợp yêu cầu"},
                {"conceptName":"C","outfitCode":"AO_BA_BA","colorCode":"CREAM","styleCode":"ELEGANT","accessories":["FAN"],"matchScore":80,"reason":"Phù hợp yêu cầu"}
            ]}
            """);
    }
    @Test void catalogAndReferencesSeeded() throws Exception {
        mvc.perform(get("/api/outfits")).andExpect(status().isOk()).andExpect(jsonPath("$",hasSize(5)));
        mvc.perform(get("/api/outfits/AO_DAI")).andExpect(status().isOk())
            .andExpect(jsonPath("$.colors",hasSize(11))).andExpect(jsonPath("$.accessories",hasSize(17)))
            .andExpect(jsonPath("$.assets",hasSize(14)))
            .andExpect(jsonPath("$.assets[?(@.assetType == 'BASE_AVATAR')]",hasSize(7)))
            .andExpect(jsonPath("$.assets[?(@.assetType == 'GARMENT')]",hasSize(7)));
        mvc.perform(get("/api/reference-data")).andExpect(status().isOk())
            .andExpect(jsonPath("$.styles",hasSize(5))).andExpect(jsonPath("$.events",hasSize(5)));
        mvc.perform(get("/api/outfits/AO_DAI/cultural-knowledge")).andExpect(status().isOk())
            .andExpect(jsonPath("$",hasSize(6)));
    }
    @Test void unknownResourcesAndBadRequests() throws Exception {
        mvc.perform(get("/api/outfits/NOPE")).andExpect(status().isNotFound());
        mvc.perform(get("/api/outfits/NOPE/cultural-knowledge")).andExpect(status().isNotFound());
        mvc.perform(get("/api/looks/99999")).andExpect(status().isNotFound());
        mvc.perform(get("/api/looks/0")).andExpect(status().isBadRequest());
        mvc.perform(get("/api/weather")).andExpect(status().isBadRequest());
        mvc.perform(get("/api/weather").param("city"," ")).andExpect(status().isBadRequest());
        mvc.perform(post("/api/cultural-score").contentType("application/json").content("{"))
            .andExpect(status().isBadRequest());
    }
    @Test void weatherUsesGateway() throws Exception {
        mvc.perform(get("/api/weather").param("city","Hanoi")).andExpect(status().isOk())
            .andExpect(jsonPath("$.temperature").value(31.5)).andExpect(jsonPath("$.humidity").value(70));
    }
    @Test void noRulesMeansNoInventedScore() throws Exception {
        mvc.perform(post("/api/cultural-score").contentType("application/json").content(SELECTION))
            .andExpect(status().isOk()).andExpect(jsonPath("$.score").value(nullValue()))
            .andExpect(jsonPath("$.level").value("INSUFFICIENT_DATA"))
            .andExpect(jsonPath("$.missingCategories",hasSize(5)));
    }
    @Test void fullWardrobeIsCheckedAndSameScoreIsPersisted() throws Exception {
        var request=(com.fasterxml.jackson.databind.node.ObjectNode)mapper.readTree(SELECTION);
        request.set("context",mapper.readTree("{\"weather\":\"mua\",\"setting\":\"ngoai_troi\",\"role\":\"be_trap\"}"));
        request.set("wardrobe",mapper.readTree("""
            {"character":"female","selection":{"shirt":"jade","pants":"ivory","shoes":"dep-crocs",
            "accessories":{"headphones":"tai-nghe"},"styles":{"shirt":{"color":"#765a94"}}}}
            """));
        when(ai.culturalScore(any())).thenReturn(mapper.readTree("""
            {"score":72,"level":"WARNING","breakdown":{"structure":80,"garmentCharacteristics":65,
            "accessories":70,"context":75,"modernRemix":60},"warnings":[],"missingCategories":[],
            "explanation":"Checked full wardrobe", "checks":[{"ruleId":"R61","title":"Wet footwear",
            "category":"CONTEXT","level":"consider","points":-12,"reason":"Outdoor rain","suggestion":"Check sole",
            "sourceVerified":false,"sourceNote":"App rule"}],"assessment":{"ruleCount":80,"matchedRuleCount":1,
            "contextUsed":{"weather":"mua"},"missingContext":["timeOfDay"],"colorMetrics":{"lightnessContrast":0.25}}}
            """));
        mvc.perform(post("/api/cultural-score").contentType("application/json").content(request.toString()))
            .andExpect(status().isOk()).andExpect(jsonPath("$.score").value(72))
            .andExpect(jsonPath("$.checks[0].ruleId").value("R61"))
            .andExpect(jsonPath("$.assessment.ruleCount").value(80));
        var saved=mvc.perform(post("/api/looks").contentType("application/json").content(request.toString()))
            .andExpect(status().isCreated()).andExpect(jsonPath("$.culturalScore").value(72)).andReturn();
        long id=mapper.readTree(saved.getResponse().getContentAsString()).path("id").asLong();
        mvc.perform(get("/api/looks/"+id)).andExpect(jsonPath("$.culturalScore").value(72));
        verify(ai,times(2)).culturalScore(argThat(value -> value instanceof com.vietphuc.remix.dto.request.LookSelection l
            && l.wardrobe().path("selection").path("styles").path("shirt").path("color").asText().equals("#765a94")
            && l.context().path("role").asText().equals("be_trap")
            && l.wardrobe().path("selection").path("accessories").path("headphones").asText().equals("tai-nghe")));
    }
    private void rule(ScoreCategory category,TargetType target,String code,int modifier,RuleType type) {
        CulturalRule r=new CulturalRule();
        r.setOutfit(outfits.findByCode("AO_DAI").orElseThrow()); r.setCategory(category);
        r.setTargetType(target); r.setTargetCode(code); r.setScoreModifier(modifier);
        r.setRuleType(type); r.setSeverity(Severity.MEDIUM); r.setMessage("Test fixture only");
        r.setSuggestion("Test fixture"); r.setSourceName("TEST ONLY"); r.setSourceUrl("https://example.test/rule");
        rules.saveAndFlush(r);
    }
    @Test void weightedScoreWarningsAndSources() throws Exception {
        rule(ScoreCategory.STRUCTURE,TargetType.OUTFIT,"AO_DAI",-5,RuleType.RECOMMENDED);
        rule(ScoreCategory.GARMENT_CHARACTERISTICS,TargetType.COLOR,"RED",-10,RuleType.RECOMMENDED);
        rule(ScoreCategory.ACCESSORIES,TargetType.ACCESSORY,"NON_LA",-22,RuleType.CAUTION);
        rule(ScoreCategory.CONTEXT,TargetType.EVENT,"FESTIVAL",-10,RuleType.RECOMMENDED);
        rule(ScoreCategory.MODERN_REMIX,TargetType.STYLE,"GEN_Z",-18,RuleType.RECOMMENDED);
        mvc.perform(post("/api/cultural-score").contentType("application/json").content(SELECTION))
            .andExpect(status().isOk()).andExpect(jsonPath("$.score").value(88))
            .andExpect(jsonPath("$.level").value("SUITABLE")).andExpect(jsonPath("$.warnings",hasSize(1)))
            .andExpect(jsonPath("$.warnings[0].sourceName").value("TEST ONLY"))
            .andExpect(jsonPath("$.breakdown.accessories").value(78));
        var result=mvc.perform(post("/api/looks").contentType("application/json").content(SELECTION))
            .andExpect(status().isCreated()).andExpect(jsonPath("$.culturalScore").value(88)).andReturn();
        long id=mapper.readTree(result.getResponse().getContentAsString()).path("id").asLong();
        mvc.perform(get("/api/looks/"+id)).andExpect(status().isOk())
            .andExpect(jsonPath("$.culturalScore").value(88)).andExpect(jsonPath("$.accessories[0]").value("NON_LA"));
    }
    @Test void scoreClampsAfterAllModifiersAndSkipsNonMatchingRules() throws Exception {
        for(var category:ScoreCategory.values()) rule(category,TargetType.OUTFIT,"AO_DAI",0,RuleType.RECOMMENDED);
        rule(ScoreCategory.STRUCTURE,TargetType.COLOR,"RED",-80,RuleType.RECOMMENDED);
        rule(ScoreCategory.STRUCTURE,TargetType.COLOR,"RED",-80,RuleType.RECOMMENDED);
        rule(ScoreCategory.STRUCTURE,TargetType.COLOR,"RED",70,RuleType.RECOMMENDED);
        rule(ScoreCategory.ACCESSORIES,TargetType.ACCESSORY,"FAN",-50,RuleType.CAUTION);
        mvc.perform(post("/api/cultural-score").contentType("application/json").content(SELECTION))
            .andExpect(status().isOk()).andExpect(jsonPath("$.score").value(73))
            .andExpect(jsonPath("$.level").value("WARNING"))
            .andExpect(jsonPath("$.breakdown.structure").value(10)).andExpect(jsonPath("$.warnings",hasSize(0)));
    }
    @Test void partialRulesDoNotProduceOverallScore() throws Exception {
        rule(ScoreCategory.CONTEXT,TargetType.EVENT,"FESTIVAL",-20,RuleType.CAUTION);
        mvc.perform(post("/api/cultural-score").contentType("application/json").content(SELECTION))
            .andExpect(status().isOk()).andExpect(jsonPath("$.score").value(nullValue()))
            .andExpect(jsonPath("$.breakdown.context").value(80)).andExpect(jsonPath("$.missingCategories",hasSize(4)));
    }
    @Test void invalidSelectionsRejectedAndNotSaved() throws Exception {
        long before=looks.count();
        for(String content:List.of(SELECTION.replace("AO_DAI","UNSUPPORTED"),
            SELECTION.replace("RED","MAGENTA"),SELECTION.replace("GEN_Z","UNKNOWN"),
            SELECTION.replace("FESTIVAL","UNKNOWN"),SELECTION.replace("NON_LA","INVALID"),
            SELECTION.replace("[\"NON_LA\"]","[\"NON_LA\",\"NON_LA\"]"),
            SELECTION.replace("[\"NON_LA\"]","null"))) {
            mvc.perform(post("/api/looks").contentType("application/json").content(content))
                .andExpect(status().isBadRequest());
        }
        assertEquals(before,looks.count());
    }
    @Test void accessoryMustBeSupportedByOutfit() throws Exception {
        var link=supported.findByOutfitCodeOrderByAccessoryCodeAsc("AO_DAI").stream()
            .filter(l -> l.getAccessory().getCode().equals("NON_LA")).findFirst().orElseThrow();
        supported.delete(link); supported.flush();
        mvc.perform(post("/api/cultural-score").contentType("application/json").content(SELECTION))
            .andExpect(status().isBadRequest());
    }
    @Test void clientCannotInjectScoresOrUnknownFields() throws Exception {
        mvc.perform(post("/api/looks").contentType("application/json")
            .content(SELECTION.strip().replace("}",",\"culturalScore\":100}")))
            .andExpect(status().isBadRequest());
    }
    @Test void recommendExactlyThreeWithAuthoritativeWeather() throws Exception {
        var data=(com.fasterxml.jackson.databind.node.ObjectNode)concepts();
        data.set("analysis",mapper.readTree("""
            {"event":"GRADUATION","style":"MINIMAL","character":"male","source":"gemini",
             "understanding":"Bạn chụp kỷ yếu ngoài trời, thích tối giản.",
             "context":{"setting":"ngoai_troi","weather":"lanh"}}
            """));
        when(ai.recommendations(any())).thenReturn(data);
        mvc.perform(post("/api/recommendations").contentType("application/json").content(RECOMMEND))
            .andExpect(status().isOk()).andExpect(jsonPath("$.concepts",hasSize(3)))
            .andExpect(jsonPath("$.analysis.event").value("GRADUATION"))
            .andExpect(jsonPath("$.analysis.understanding").value("Bạn chụp kỷ yếu ngoài trời, thích tối giản."))
            .andExpect(jsonPath("$.analysis.character").value("male"))
            .andExpect(jsonPath("$.analysis.context.setting").value("ngoai_troi"))
            .andExpect(jsonPath("$.analysis.weather.temperature").value(31.5));
        verify(ai).recommendations(argThat(p -> p instanceof Map<?,?> m && m.containsKey("referenceData") && m.containsKey("culturalContext")));
    }
    @Test void rejectWrongConceptCountAndInvalidAiCodesAndTypes() throws Exception {
        var wrongCount=mapper.createObjectNode().set("concepts",mapper.createArrayNode());
        when(ai.recommendations(any())).thenReturn(wrongCount);
        mvc.perform(post("/api/recommendations").contentType("application/json").content(RECOMMEND))
            .andExpect(status().isBadGateway()).andExpect(jsonPath("$.code").value("INVALID_AI_OUTPUT"));
        for(String replacement:List.of("\"outfitCode\":\"NOPE\"","\"outfitCode\":null")) {
            when(ai.recommendations(any())).thenReturn(mapper.readTree(concepts().toString()
                .replace("\"outfitCode\":\"AO_DAI\"",replacement)));
            mvc.perform(post("/api/recommendations").contentType("application/json").content(RECOMMEND))
                .andExpect(status().isBadGateway());
        }
        for(String replacement:List.of("101","92.5","\"92\"","null")) {
            when(ai.recommendations(any())).thenReturn(mapper.readTree(concepts().toString().replace("\"matchScore\":92","\"matchScore\":"+replacement)));
            mvc.perform(post("/api/recommendations").contentType("application/json").content(RECOMMEND))
                .andExpect(status().isBadGateway());
        }
    }
    @Test void rejectInvalidInterpretationAndForwardExplicitContext() throws Exception {
        var data=(com.fasterxml.jackson.databind.node.ObjectNode)concepts();
        data.set("analysis",mapper.readTree("""
            {"event":"NOPE","style":"MINIMAL","character":"male","source":"gemini",
             "understanding":"Khách dự cưới.","context":{"role":"khach"}}
            """));
        when(ai.recommendations(any())).thenReturn(data);
        var request=(com.fasterxml.jackson.databind.node.ObjectNode)mapper.readTree(RECOMMEND);
        request.set("context",mapper.readTree("{\"role\":\"khach\",\"setting\":\"trong_nha\"}"));
        mvc.perform(post("/api/recommendations").contentType("application/json").content(request.toString()))
            .andExpect(status().isBadGateway()).andExpect(jsonPath("$.code").value("INVALID_AI_OUTPUT"));
        verify(ai).recommendations(argThat(p -> p instanceof Map<?,?> m && m.get("context") instanceof JsonNode context
            && context.path("role").asText().equals("khach") && context.path("setting").asText().equals("trong_nha")));
    }
    @Test void invalidRecommendationContextDoesNotCallUpstreams() throws Exception {
        mvc.perform(post("/api/recommendations").contentType("application/json").content(RECOMMEND.replace("GEN_Z","NOPE")))
            .andExpect(status().isBadRequest());
        verifyNoInteractions(ai); verify(weather,never()).current(anyString());
    }
    @Test void remixAndSaveCompleteFlow() throws Exception {
        when(ai.recommendations(any())).thenReturn(concepts());
        var result=mvc.perform(post("/api/recommendations").contentType("application/json").content(RECOMMEND))
            .andExpect(status().isOk()).andReturn();
        assertEquals("AO_DAI",mapper.readTree(result.getResponse().getContentAsString()).path("concepts").get(0).path("outfitCode").asText());
        when(ai.remix(any())).thenReturn(mapper.readTree("""
            {"changes":{"colorCode":"DARK_RED","styleCode":"GEN_Z","removeAccessories":["NON_LA"],"addAccessories":["MINIMAL_BAG"]},"explanation":"Giữ sắc đỏ và thay phụ kiện"}
            """));
        mvc.perform(post("/api/remix").contentType("application/json")
            .content("{\"currentLook\":"+SELECTION+",\"prompt\":\"Cho outfit trẻ hơn, vẫn giữ màu đỏ\"}"))
            .andExpect(status().isOk()).andExpect(jsonPath("$.changes.colorCode").value("DARK_RED"));
        String finalLook=SELECTION.replace("\"RED\"","\"DARK_RED\"").replace("NON_LA","MINIMAL_BAG");
        mvc.perform(post("/api/cultural-score").contentType("application/json").content(finalLook)).andExpect(status().isOk());
        var saved=mvc.perform(post("/api/looks").contentType("application/json").content(finalLook))
            .andExpect(status().isCreated()).andExpect(header().exists("Location")).andReturn();
        mvc.perform(get(saved.getResponse().getHeader("Location"))).andExpect(status().isOk())
            .andExpect(jsonPath("$.colorCode").value("DARK_RED")).andExpect(jsonPath("$.accessories[0]").value("MINIMAL_BAG"));
    }
    @Test void rejectInvalidRemixOperations() throws Exception {
        String request="{\"currentLook\":"+SELECTION+",\"prompt\":\"Remix\"}";
        for(String response:List.of(
            "{\"changes\":{\"removeAccessories\":[\"FAN\"],\"addAccessories\":[]},\"explanation\":\"x\"}",
            "{\"changes\":{\"removeAccessories\":[],\"addAccessories\":[\"NOPE\"]},\"explanation\":\"x\"}",
            "{\"changes\":{\"removeAccessories\":[\"NON_LA\"],\"addAccessories\":[\"NON_LA\"]},\"explanation\":\"x\"}",
            "{\"changes\":{\"colorCode\":\"MAGENTA\",\"removeAccessories\":[],\"addAccessories\":[]},\"explanation\":\"x\"}",
            "{\"changes\":{\"removeAccessories\":[],\"addAccessories\":[\"NON_LA\"]},\"explanation\":\"x\"}")) {
            when(ai.remix(any())).thenReturn(mapper.readTree(response));
            mvc.perform(post("/api/remix").contentType("application/json").content(request)).andExpect(status().isBadGateway());
        }
    }
    @Test void allowedOriginCors() throws Exception {
        mvc.perform(options("/api/looks").header("Origin","http://localhost:5173")
            .header("Access-Control-Request-Method","POST"))
            .andExpect(status().isOk()).andExpect(header().string("Access-Control-Allow-Origin","http://localhost:5173"));
        mvc.perform(options("/api/looks").header("Origin","https://unknown.test")
            .header("Access-Control-Request-Method","POST")).andExpect(status().isForbidden());
    }
}
