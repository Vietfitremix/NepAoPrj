package com.vietphuc.remix.repository;
import com.vietphuc.remix.entity.*;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
public interface CulturalRuleRepository extends JpaRepository<CulturalRule,Long> { List<CulturalRule> findByOutfitCodeOrderByIdAsc(String code); }
