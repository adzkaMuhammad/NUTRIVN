import axios from "axios";

const BASE = process.env.REACT_APP_BACKEND_URL;
export const api = axios.create({ baseURL: `${BASE}/api` });

export const getHome = () => api.get("/home").then((r) => r.data);
export const getRecipes = (params) => api.get("/recipes", { params }).then((r) => r.data);
export const getRecipe = (slug) => api.get(`/recipes/${slug}`).then((r) => r.data);
export const getCategories = () => api.get("/categories").then((r) => r.data);
export const getMoods = () => api.get("/moods").then((r) => r.data);
export const getMood = (key) => api.get(`/moods/${key}`).then((r) => r.data);
export const getInsight = (slug) => api.get(`/insight/${slug}`).then((r) => r.data);
export const postScan = (body) => api.post("/scan", body).then((r) => r.data);
