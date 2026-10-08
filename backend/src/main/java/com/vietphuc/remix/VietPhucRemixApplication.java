package com.vietphuc.remix;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
@SpringBootApplication
@ConfigurationPropertiesScan
public class VietPhucRemixApplication {
    public static void main(String[] args) { SpringApplication.run(VietPhucRemixApplication.class, args); }
}
