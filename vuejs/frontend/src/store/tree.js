import { createStore } from 'vuex'

export default createStore({
  state: {
    treeobject:[]
  },
  getters: {
  },
  mutations: {
    addTreeObject(state,id,child_array_data){
      console.log(state,id,child_array_data)
    }
  },
  actions: {
  },
  modules: {
  }
})
