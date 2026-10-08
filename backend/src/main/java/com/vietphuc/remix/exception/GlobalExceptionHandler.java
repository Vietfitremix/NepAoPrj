package com.vietphuc.remix.exception;
import java.time.Instant;
import java.util.*;
import org.slf4j.*;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.method.annotation.HandlerMethodValidationException;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.servlet.resource.NoResourceFoundException;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.MissingServletRequestParameterException;
@RestControllerAdvice
public class GlobalExceptionHandler {
    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);
    public record ErrorResponse(String code, String message, Map<String,String> fields, Instant timestamp) {}
    private ResponseEntity<ErrorResponse> error(HttpStatus status, String code, String message, Map<String,String> fields) {
        return ResponseEntity.status(status).body(new ErrorResponse(code, message, fields, Instant.now()));
    }
    @ExceptionHandler(ApiException.class)
    ResponseEntity<ErrorResponse> api(ApiException e) { return error(e.getStatus(),e.getCode(),e.getMessage(),Map.of()); }
    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<ErrorResponse> validation(MethodArgumentNotValidException e) {
        Map<String,String> fields = new TreeMap<>();
        e.getBindingResult().getFieldErrors().forEach(f -> fields.putIfAbsent(f.getField(),f.getDefaultMessage()));
        return error(HttpStatus.BAD_REQUEST,"VALIDATION_ERROR","Dữ liệu đầu vào không hợp lệ.",fields);
    }
    @ExceptionHandler({HttpMessageNotReadableException.class, MethodArgumentTypeMismatchException.class,
        MissingServletRequestParameterException.class, HandlerMethodValidationException.class})
    ResponseEntity<ErrorResponse> malformed(Exception e) {
        return error(HttpStatus.BAD_REQUEST,"INVALID_REQUEST","Kiểm tra JSON, tham số và kiểu dữ liệu đầu vào.",Map.of());
    }
    @ExceptionHandler(NoResourceFoundException.class)
    ResponseEntity<ErrorResponse> missing(Exception e) {
        return error(HttpStatus.NOT_FOUND,"NOT_FOUND","Không tìm thấy API.",Map.of());
    }
    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    ResponseEntity<ErrorResponse> method(Exception e) {
        return error(HttpStatus.METHOD_NOT_ALLOWED,"METHOD_NOT_ALLOWED","Phương thức HTTP không được hỗ trợ.",Map.of());
    }
    @ExceptionHandler(Exception.class)
    ResponseEntity<ErrorResponse> unexpected(Exception e) {
        log.error("Unexpected backend error: {}", e.getClass().getSimpleName());
        return error(HttpStatus.INTERNAL_SERVER_ERROR,"INTERNAL_ERROR","Không thể xử lý yêu cầu.",Map.of());
    }
}
