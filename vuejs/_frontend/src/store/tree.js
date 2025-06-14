import { createStore } from 'vuex'

export default createStore({
  state: {
    tree_right_click_menu_position:{
      x:0,
      y:0
    },
    tree_right_click_menu_visible:false,
    tree_header_list_visible:false,
    select_object:{ id: "", group_id: "", deep_level: "", parent_id: "", code_id: "" },
    material_list:[{id:"",name:""}],
    add_target_code:{id:"",code_id:""},
    new_object:{ id: "", group_id: "", deep_level: "", parent_id: "", code_id: "" },
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
    ReleaseObject(state){
      state.select_object = { id: "", group_id: "", deep_level: "", parent_id: "", code_id: "" }
    },
    ShowHeaderList(state){
      //ヘッダー一覧コンポーネントを表示するか管理するフラグ
      state.tree_header_list_visible = true;//メニュー２を開く
    },
    HideHeaderList(state){
      //ヘッダー一覧コンポーネントを表示するか管理するフラグ
      state.tree_header_list_visible = false;
    },
    TreeRightClickMenuSetPosition(state,pyload){
      //x,yの座標を管理するメソッド
      state.tree_right_click_menu_position.x = pyload.x;
      state.tree_right_click_menu_position.y = pyload.y;
    },
    SetMaterial(state,pyload){
      const mate_array = pyload
      state.material_list = [];//配列リセット
      mate_array.forEach(m => {
        state.material_list.push({id:m.id, name:m.code_header})        
      });
    },
    SetAddTarget(state,pyload){
      //maxCodeで取得した値をセット
      state.add_target_code = {
        id: pyload.id,
        code_id: pyload.code_id
      }
    },
    SetNewObject(state,pyload){
      state.new_object.id = pyload.id;
      state.new_object.group_id = pyload.group_id;
      state.new_object.deep_level = pyload.deep_level;
      state.new_object.parent_id = pyload.parent_id;
      state.new_object.code_id = pyload.code_id;
    },
    SetEmptyNewObject(state){
      state.new_object.id ="";
      state.new_object.group_id ="";
      state.new_object.deep_level ="";
      state.new_object.parent_id ="";
      state.new_object.code_id ="";
    }
  },
  actions: {
  },
  modules: {
  }
})
