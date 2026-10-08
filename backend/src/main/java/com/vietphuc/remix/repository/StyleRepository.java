package com.vietphuc.remix.repository;
import com.vietphuc.remix.entity.Style;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.*;
public interface StyleRepository extends JpaRepository<Style,Long> {
    Optional<Style> findByCode(String code);
    List<Style> findAllByOrderByIdAsc();
}
