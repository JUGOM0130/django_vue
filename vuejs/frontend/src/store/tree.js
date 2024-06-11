import { createStore } from 'vuex'

export default createStore({
  state: {

    tree_right_click_menu_visible:false,
    select_object:{ id: "", group_id: "", deep_level: "", parent_id: "", code_id: "" }
  },
  getters: {
    getRightClickMenuVisible(state){
      return state.tree_right_click_menu_visible
    }
  },
  mutations: {
    TreeRightClickMenuShow(state){
      state.tree_right_click_menu_visible = true;
    },
    TreeRightClickMenuHide(state){
      state.tree_right_click_menu_visible = false;
    },
    SetObject(state,pyload){
      state.select_object.id = pyload.id;
      state.select_object.group_id = pyload.group_id;
      state.select_object.deep_level = pyload.deep_level;
      state.select_object.parent_id = pyload.parent_id;
      state.select_object.code_id = pyload.code_id;

    },
    releaseObject(state){
      state.select_object = { id: "", group_id: "", deep_level: "", parent_id: "", code_id: "" }
    }
  },
  actions: {
  },
  modules: {
  }
})
