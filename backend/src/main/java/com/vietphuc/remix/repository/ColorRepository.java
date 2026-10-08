package com.vietphuc.remix.repository;
import com.vietphuc.remix.entity.Color;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.*;
public interface ColorRepository extends JpaRepository<Color,Long> {
    Optional<Color> findByCode(String code);
    List<Color> findAllByOrderByIdAsc();
}
