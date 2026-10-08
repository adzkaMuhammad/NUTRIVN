export const NAV = {
  home: "nav-home",
  scan: "nav-scan",
  recipes: "nav-recipes",
  mood: "nav-mood",
};

export const HOME = {
  brand: "brand-logo",
  insightCta: "home-insight-cta",
  scanCta: "home-scan-cta",
  moodItem: (k) => `home-mood-${k}`,
  pickCard: (s) => `home-pick-${s}`,
  seeAllMoods: "home-see-all-moods",
  seeAllPicks: "home-see-all-picks",
};

export const SCAN = {
  back: "scan-back",
  benchmark: (s) => `scan-benchmark-${s}`,
  measureToggle: "scan-measure-toggle",
  startBtn: "scan-start-btn",
  uploadInput: "scan-upload-input",
  resultCard: "scan-result-card",
  resultSpice: "scan-result-spice",
  resetBtn: "scan-reset-btn",
};

export const RECIPES = {
  search: "recipes-search",
  filter: (k) => `recipes-filter-${k}`,
  card: (s) => `recipes-card-${s}`,
};

export const DETAIL = {
  back: "detail-back",
  scanThis: "detail-scan-this",
  spiceRow: (n) => `detail-spice-${n}`,
  insight: "detail-insight",
};

export const MOOD = {
  option: (k) => `mood-option-${k}`,
  recipe: (s) => `mood-recipe-${s}`,
  seeAll: "mood-see-all",
};
