package com.vietphuc.remix.repository;
import com.vietphuc.remix.entity.Outfit;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.*;
public interface OutfitRepository extends JpaRepository<Outfit,Long> {
    Optional<Outfit> findByCode(String code);
    List<Outfit> findAllByOrderByIdAsc();
}
