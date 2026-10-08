package com.vietphuc.remix.repository;
import com.vietphuc.remix.entity.*;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
public interface CulturalKnowledgeRepository extends JpaRepository<CulturalKnowledge,Long> { List<CulturalKnowledge> findByOutfitCodeOrderByIdAsc(String code); }
