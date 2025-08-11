# IBM Granite 3.3-8b-alora-uncertainty Model Documentation

## Overview

The IBM Granite 3.3-8b-alora-uncertainty model is part of the Granite family of foundation models developed by IBM Research. This model is specifically designed to provide calibrated certainty scores when answering questions, making it ideal for applications where confidence in AI-generated responses is critical, such as our Smart Travel Planner application.

<mcreference link="https://huggingface.co/ibm-granite" index="1">1</mcreference>

## Key Features

### Uncertainty Quantification

The model provides calibrated certainty scores that indicate its confidence in the generated responses. These scores are quantized to 10 possible values (5%, 15%, 25%, ..., 95%) and are calibrated such that given a set of answers assigned a certainty score of X%, approximately X% of these answers should be correct. <mcreference link="https://huggingface.co/ibm-granite/granite-3.2-8b-lora-uncertainty" index="2">2</mcreference>

### Activated LoRA Architecture

The model uses Activated LoRA (aLoRA), a low-rank adapter architecture that allows for reusing existing base model KV cache for more efficient inference. This architecture enables the model to provide uncertainty quantification while maintaining the full capabilities of the base model. <mcreference link="https://huggingface.co/ibm-granite/granite-3.2-8b-alora-uncertainty" index="5">5</mcreference>

### Integration with Smart Travel Planner

In our Smart Travel Planner application, the IBM Granite 3.3-8b-alora-uncertainty model is used for:

1. **Traffic Density Classification**: Classifying traffic density at major intersections, highway segments, and urban streets as Low, Medium, or High with associated confidence levels.

2. **Route Optimization**: Analyzing multiple possible routes between origin and destination, considering factors like current traffic conditions, road quality, and historical congestion patterns.

3. **Departure Time Recommendation**: Analyzing traffic patterns throughout the day to identify time periods with minimal congestion and recommend optimal departure times with confidence levels.

4. **Traffic Incident Analysis**: Analyzing the impact of current incidents on travel time, predicting how long incidents might affect traffic, and suggesting alternative routes.

5. **Location-Specific Insights**: Providing insights specific to Indian cities and regions, considering local traffic patterns, peak hours, and common congestion points.

## Usage in the Application

The model is integrated into our application through the IBM Watsonx AI platform. The system prompt and training data structure have been customized for traffic analysis in the Indian context, enabling the model to provide accurate and relevant insights for travelers in India.

### System Prompt

We use a specialized system prompt that instructs the model to analyze traffic data and provide insights on traffic density, route optimization, departure time recommendations, traffic incident analysis, and location-specific insights for Indian cities and regions.

### Input Format

The model accepts input in the following format:

```json
{
  "origin": "String - Origin location name",
  "destination": "String - Destination location name",
  "traffic_data": {
    "route_summary": "Object - Summary of route details",
    "incidents": "Array - Traffic incidents along the route",
    "traffic_patterns": "Object - Traffic patterns at different times"
  }
}
```

### Output Format

The model generates output in the following format:

```json
{
  "html_content": "String - HTML formatted analysis for display",
  "density_levels": "Object - Traffic density classifications",
  "optimal_departure": "String - Recommended departure time",
  "confidence_score": "Float - Confidence level of the analysis (0-1)"
}
```

## Benefits for Smart Travel Planner

1. **Enhanced User Trust**: By providing certainty scores, users can better understand when to trust the AI's recommendations.

2. **Improved Decision Making**: The model's ability to quantify uncertainty helps users make more informed travel decisions.

3. **Adaptive Routing**: The model can suggest alternative routes when it has low confidence in the primary route due to uncertain traffic conditions.

4. **Contextual Understanding**: The model is trained to understand the specific context of Indian traffic patterns and road conditions.

## References

1. IBM Granite Organization on Hugging Face: [https://huggingface.co/ibm-granite](https://huggingface.co/ibm-granite)
2. Granite 3.2-8b-lora-uncertainty: [https://huggingface.co/ibm-granite/granite-3.2-8b-lora-uncertainty](https://huggingface.co/ibm-granite/granite-3.2-8b-lora-uncertainty)
3. Granite 3.0-8b-lora-uncertainty: [https://huggingface.co/ibm-granite/granite-uncertainty-3.0-8b-lora](https://huggingface.co/ibm-granite/granite-uncertainty-3.0-8b-lora)
4. IBM Granite Official Page: [https://www.ibm.com/granite](https://www.ibm.com/granite)
5. Granite 3.2-8b-alora-uncertainty: [https://huggingface.co/ibm-granite/granite-3.2-8b-alora-uncertainty](https://huggingface.co/ibm-granite/granite-3.2-8b-alora-uncertainty)