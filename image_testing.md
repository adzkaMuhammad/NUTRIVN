# NutriVane image integration testing rules

## Image handling rules
- Always use base64-encoded images for all tests and requests.
- Accepted formats: JPEG, PNG, WEBP only.
- Do not use SVG, BMP, HEIC, or other formats.
- Do not upload blank, solid-color, or uniform-variance images.
- Every image must contain real visual features (objects, edges, textures, shadows).
- If not PNG/JPEG/WEBP, transcode to PNG or JPEG before upload; re-detect MIME after transforms.
- If animated (GIF/APNG/animated WEBP), extract first frame only.
- Resize large images to reasonable bounds (avoid oversized payloads).

## NutriVane endpoints using AI
- POST /api/scan with {benchmark_slug, measure, image_base64} — vision model (Gemini 3.1 Pro) runs ONLY when image_base64 is present.
- GET /api/insight/{slug} — text model (Gemini 3 Flash), cached in Mongo.
