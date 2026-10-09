package com.vietphuc.remix.controller;

import com.vietphuc.remix.exception.ApiException;
import java.time.Duration;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.context.request.WebRequest;

@RestController @RequiredArgsConstructor
public class AssetFileController {
    private final JdbcTemplate jdbc;
    @GetMapping("/figure/{*path}")
    public ResponseEntity<byte[]> figure(@PathVariable String path,WebRequest request) {
        return file("frontend/public/figure/"+path.replaceFirst("^/+",""),request);
    }
    @GetMapping("/api/assets/{*path}")
    public ResponseEntity<byte[]> source(@PathVariable String path,WebRequest request) {
        return file(path.replaceFirst("^/+",""),request);
    }
    private ResponseEntity<byte[]> file(String path,WebRequest request) {
        if(path.contains("\\") || path.indexOf('\0')>=0 || java.util.Arrays.asList(path.split("/")).contains(".."))
            throw ApiException.notFound("Không tìm thấy asset.");
        // Only an exact database key is accessible. No filesystem paths are opened.
        var metadata=jdbc.queryForList("SELECT content_type,sha256,byte_size FROM asset_files WHERE relative_path=?",path);
        if(metadata.isEmpty())throw ApiException.notFound("Không tìm thấy asset.");
        var row=metadata.getFirst();
        String etag="\""+row.get("sha256")+"\"";
        if(request.checkNotModified(etag))return ResponseEntity.status(HttpStatus.NOT_MODIFIED).eTag(etag).build();
        byte[] bytes=jdbc.queryForObject("SELECT file_data FROM asset_files WHERE relative_path=?",byte[].class,path);
        return ResponseEntity.ok().contentType(MediaType.parseMediaType(row.get("content_type").toString()))
            .contentLength(((Number)row.get("byte_size")).longValue()).eTag(etag)
            .cacheControl(CacheControl.maxAge(Duration.ofHours(1)).cachePublic()).body(bytes);
    }
}
