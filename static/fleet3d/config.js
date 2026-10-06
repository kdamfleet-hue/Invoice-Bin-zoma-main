// Fleet 3D live configuration. The page is served by the same Flask origin as the API.
window.FLEET_CONFIG = {
  apiUrl: "/api/gps",
  pollIntervalMs: 12000,
  center: { lat: 26.4207, lng: 50.0888 },
  worldScale: 0.02,
  useMockOnError: false,
  mockVehicleCount: 0,
  speed: { warn: 90, danger: 120 },
  trail: { enabled: true, maxPoints: 80, sampleMs: 300 },
  // Load the current active geofences from /api/gps/geofences; do not use prototype coordinates.
  zones: [],
};
