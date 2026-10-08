package com.vietphuc.remix.repository;
import com.vietphuc.remix.entity.Accessory;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.*;
public interface AccessoryRepository extends JpaRepository<Accessory,Long> {
    Optional<Accessory> findByCode(String code);
    List<Accessory> findAllByOrderByIdAsc();
}
