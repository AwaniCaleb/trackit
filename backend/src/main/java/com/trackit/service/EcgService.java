package com.trackit.service;

import com.trackit.dto.EcgRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class EcgService {

    @Value("${app.ml.url}")
    private String mlUrl;

    private final RestTemplate restTemplate;

    public Map<?, ?> analyse(EcgRequest req) {
        try {
            return restTemplate.postForObject(mlUrl + "/analyse", req, Map.class);
        } catch (Exception e) {
            // ML service unavailable — return graceful degraded response
            return Map.of(
                "classification", "Unavailable",
                "confidence", 0.0,
                "error", "ML service offline"
            );
        }
    }
}
