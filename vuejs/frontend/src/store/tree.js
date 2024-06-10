import { createStore } from 'vuex'

export default createStore({
  state: {
    
    tree_right_click_menu_visible:false
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
    }
  },
  actions: {
  },
  modules: {
  }
})
