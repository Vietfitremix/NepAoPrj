package com.vietphuc.remix.repository;
import com.vietphuc.remix.entity.*;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
public interface LookAccessoryRepository extends JpaRepository<LookAccessory,LookAccessoryId> { List<LookAccessory> findByLookIdOrderByAccessoryLayerOrderAsc(Long id); }
