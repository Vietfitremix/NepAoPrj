package com.vietphuc.remix.repository;
import com.vietphuc.remix.entity.Event;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.*;
public interface EventRepository extends JpaRepository<Event,Long> {
    Optional<Event> findByCode(String code);
    List<Event> findAllByOrderByIdAsc();
}
