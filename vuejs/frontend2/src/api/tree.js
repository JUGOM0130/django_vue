// tree.js
import axios from "./settings";

export const getAllTree = () => {
  return axios.get("/trees/");
};

export const getTree = (id) => {
  return axios.get(`/trees/${id}/`);
};

export const createTree = (data) => {
  return axios.post("/trees/", data);
};

export const updateTree = (id, data) => {
  return axios.put(`/trees/${id}/`, data);
};

export const deleteTree = (id) => {
  return axios.delete(`/trees/${id}/`);
};