package com.vietphuc.remix.repository;
import com.vietphuc.remix.entity.*;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
public interface OutfitAssetRepository extends JpaRepository<OutfitAsset,Long> { List<OutfitAsset> findByOutfitCodeOrderByLayerOrderAsc(String code); }
