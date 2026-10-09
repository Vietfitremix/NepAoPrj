package com.vietphuc.remix;

import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest @AutoConfigureMockMvc @ActiveProfiles("test")
class WebHostingTest {
    @TempDir static Path folder;
    @Autowired MockMvc mvc;
    @DynamicPropertySource static void properties(DynamicPropertyRegistry registry) {
        registry.add("app.web-root", () -> folder.resolve("web").toString());
    }
    @BeforeAll static void writeBuildFixture() throws Exception {
        Files.createDirectories(folder.resolve("web/assets"));
        Files.writeString(folder.resolve("web/index.html"), "<html>React build fixture</html>");
        Files.writeString(folder.resolve("web/assets/site.css"), "body{color:red}");
        Files.writeString(folder.resolve("private.txt"), "outside web root");
    }
    @Test void spaRoutesServeIndexAndStaticFiles() throws Exception {
        mvc.perform(get("/mix/saved-42")).andExpect(status().isOk()).andExpect(content().string("<html>React build fixture</html>"));
        mvc.perform(get("/assets/site.css")).andExpect(status().isOk()).andExpect(content().string("body{color:red}"));
        mvc.perform(get("/")).andExpect(forwardedUrl("/index.html"));
    }
    @Test void missingApiAndAssetsDoNotReturnSpaHtml() throws Exception {
        for (String path : new String[]{"/api/not-a-route", "/assets/missing.js", "/figure/missing.png"})
            mvc.perform(get(path)).andExpect(status().isNotFound());
    }
    @Test void resourcesOutsideWebRootCannotBeRead() throws Exception {
        mvc.perform(get("/../private.txt")).andExpect(status().isNotFound());
    }
}
