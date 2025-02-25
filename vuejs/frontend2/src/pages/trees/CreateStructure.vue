<script setup>
import { getTree } from '@/api/tree';
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';



const router = useRoute();
const errorMessage = ref('');
const id = ref('');
const name = ref('');

const fetchTrees = async (id) => {
  try {
    const response = await getTree(id);
    name.value = response.data.name;
  } catch (error) {
    console.error("Error fetching tree data:", error);
    errorMessage.value = 'Failed to load tree data. Please try again later.';
  }
};

onMounted(async () => {
    id.value = router.query.id;
    if (id.value) {
        await fetchTrees(id.value);
    } else {
        errorMessage.value = 'Tree ID is missing.';
    }
});
</script>

<template>
  <v-container>
    <!--エラーの場合-->
    <p v-if="errorMessage">{{ errorMessage }}</p>

    <!--正常な場合-->
    <p v-else>{{ id }} - {{ name }}</p>
  </v-container>
</template>
