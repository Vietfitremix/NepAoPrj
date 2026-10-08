package com.vietphuc.remix.service;
import com.vietphuc.remix.entity.*;
import com.vietphuc.remix.dto.request.LookSelection;
import com.vietphuc.remix.repository.*;
import com.vietphuc.remix.exception.ApiException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.*;
@Service @RequiredArgsConstructor @Transactional(readOnly=true)
public class SelectionService {
    private final OutfitRepository outfits;
    private final ColorRepository colors;
    private final StyleRepository styles;
    private final EventRepository events;
    private final AccessoryRepository accessories;
    private final OutfitAccessoryRepository supported;
    public record Selection(Outfit outfit,Color color,Style style,Event event,List<Accessory> accessories) {}
    public void validateContext(String eventCode,String styleCode) { event(eventCode); style(styleCode); }
    public Event event(String code) {
        return events.findByCode(code).orElseThrow(() -> ApiException.invalid("Mã sự kiện không được hỗ trợ: "+code));
    }
    public Style style(String code) {
        return styles.findByCode(code).orElseThrow(() -> ApiException.invalid("Mã phong cách không được hỗ trợ: "+code));
    }
    public Selection validate(LookSelection look) {
        var outfit=outfits.findByCode(look.outfitCode()).orElseThrow(() -> ApiException.invalid("Mã trang phục không được hỗ trợ."));
        var color=colors.findByCode(look.colorCode()).orElseThrow(() -> ApiException.invalid("Mã màu không được hỗ trợ."));
        if(look.accessories()==null || new HashSet<>(look.accessories()).size()!=look.accessories().size())
            throw ApiException.invalid("Danh sách phụ kiện bị thiếu hoặc có mã trùng.");
        Set<String> allowed=new HashSet<>();
        supported.findByOutfitCodeOrderByAccessoryCodeAsc(outfit.getCode()).forEach(a -> allowed.add(a.getAccessory().getCode()));
        List<Accessory> selected=new ArrayList<>();
        for(String code:look.accessories()) {
            if(!allowed.contains(code)) throw ApiException.invalid("Phụ kiện không được hỗ trợ cho trang phục: "+code);
            selected.add(accessories.findByCode(code).orElseThrow(() -> ApiException.invalid("Mã phụ kiện không tồn tại.")));
        }
        return new Selection(outfit,color,style(look.styleCode()),event(look.eventCode()),List.copyOf(selected));
    }
}
