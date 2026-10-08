package com.vietphuc.remix.repository;
import com.vietphuc.remix.entity.*;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
public interface OutfitAccessoryRepository extends JpaRepository<OutfitAccessory,OutfitAccessoryId> { List<OutfitAccessory> findByOutfitCodeOrderByAccessoryCodeAsc(String code); }
