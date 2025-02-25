// node.js
import axios from "./settings";

export const getAllNode = () => {
  return axios.get("/node/");
};

export const getNode = (id) => {
  return axios.get(`/node/${id}/`);
};

export const createNode = (data) => {
  return axios.post("/node/", data);
};

export const updateNode = (id, data) => {
  return axios.put(`/node/${id}/`, data);
};

export const deleteNode = (id) => {
  return axios.delete(`/node/${id}/`);
};