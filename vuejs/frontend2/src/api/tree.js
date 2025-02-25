// tree.js
import axios from "./settings";

export const getAllTree = () => {
  return axios.get("/tree/");
};

export const getTree = (id) => {
  return axios.get(`/tree/${id}/`);
};

export const createTree = (data) => {
  return axios.post("/tree/", data);
};

export const updateTree = (id, data) => {
  return axios.put(`/tree/${id}/`, data);
};

export const deleteTree = (id) => {
  return axios.delete(`/tree/${id}/`);
};