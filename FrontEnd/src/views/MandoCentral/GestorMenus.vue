<script setup>
import { ref, onMounted } from 'vue';
import { fetchRoles } from '@/service/api';
import defaultMenuData from '@/config/menu.json';
import { useToast } from 'primevue/usetoast';

const toast = useToast();
const menuData = ref([]);
const rolesList = ref([]);
const isLoadingRoles = ref(true);

// Modal state
const displayEditDialog = ref(false);
const editMode = ref(''); // 'category' or 'item'
const editingCategoryIndex = ref(-1);
const editingItemIndex = ref(-1);
const formData = ref({});

// Load data on mount
onMounted(async () => {
    // 1. Load Menu Config
    const savedConfig = localStorage.getItem('nexusMenuConfig');
    if (savedConfig) {
        try {
            menuData.value = JSON.parse(savedConfig);
        } catch (e) {
            menuData.value = JSON.parse(JSON.stringify(defaultMenuData));
        }
    } else {
        menuData.value = JSON.parse(JSON.stringify(defaultMenuData));
    }

    // 2. Load Roles
    try {
        const response = await fetchRoles();
        if (response.success && response.data) {
            // Map roles for MultiSelect
            rolesList.value = response.data.map(r => ({ name: r.nombre, code: r.nombre }));
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los roles de la base de datos', life: 3000 });
        }
    } catch (e) {
        console.error(e);
        toast.add({ severity: 'error', summary: 'Error', detail: 'Fallo al conectar con el servidor para roles', life: 3000 });
    } finally {
        isLoadingRoles.value = false;
    }
});

// -- Actions: Save
const saveConfig = () => {
    localStorage.setItem('nexusMenuConfig', JSON.stringify(menuData.value));
    toast.add({ severity: 'success', summary: 'Éxito', detail: 'Configuración guardada en tu navegador. Recarga para ver cambios.', life: 4000 });
};

const resetToDefault = () => {
    localStorage.removeItem('nexusMenuConfig');
    menuData.value = JSON.parse(JSON.stringify(defaultMenuData));
    toast.add({ severity: 'info', summary: 'Restaurado', detail: 'Se ha restaurado el menú por defecto.', life: 3000 });
}

// -- Actions: Reorder Categories --
const moveCategoryUp = (index) => {
    if (index > 0) {
        const temp = menuData.value[index];
        menuData.value[index] = menuData.value[index - 1];
        menuData.value[index - 1] = temp;
    }
};

const moveCategoryDown = (index) => {
    if (index < menuData.value.length - 1) {
        const temp = menuData.value[index];
        menuData.value[index] = menuData.value[index + 1];
        menuData.value[index + 1] = temp;
    }
};

// -- Actions: Reorder Items --
const moveItemUp = (catIndex, itemIndex) => {
    const items = menuData.value[catIndex].items;
    if (itemIndex > 0) {
        const temp = items[itemIndex];
        items[itemIndex] = items[itemIndex - 1];
        items[itemIndex - 1] = temp;
    }
};

const moveItemDown = (catIndex, itemIndex) => {
    const items = menuData.value[catIndex].items;
    if (itemIndex < items.length - 1) {
        const temp = items[itemIndex];
        items[itemIndex] = items[itemIndex + 1];
        items[itemIndex + 1] = temp;
    }
};

// -- Actions: Edit --
const openEditCategory = (catIndex) => {
    editMode.value = 'category';
    editingCategoryIndex.value = catIndex;
    const cat = menuData.value[catIndex];
    formData.value = {
        label: cat.label,
        icon: cat.icon,
        roles: cat.roles ? cat.roles.map(r => ({ name: r, code: r })) : []
    };
    displayEditDialog.value = true;
};

const openEditItem = (catIndex, itemIndex) => {
    editMode.value = 'item';
    editingCategoryIndex.value = catIndex;
    editingItemIndex.value = itemIndex;
    const item = menuData.value[catIndex].items[itemIndex];
    formData.value = {
        label: item.label,
        title: item.title || item.label,
        icon: item.icon,
        to: item.to,
        componentPath: item.componentPath,
        roles: item.roles ? item.roles.map(r => ({ name: r, code: r })) : []
    };
    displayEditDialog.value = true;
};

const saveEdit = () => {
    const roleStrings = formData.value.roles.map(r => r.code);

    if (editMode.value === 'category') {
        const cat = menuData.value[editingCategoryIndex.value];
        cat.label = formData.value.label;
        cat.icon = formData.value.icon;
        if (roleStrings.length > 0) {
            cat.roles = roleStrings;
        } else {
            delete cat.roles;
        }
    } else {
        const item = menuData.value[editingCategoryIndex.value].items[editingItemIndex.value];
        item.label = formData.value.label;
        item.title = formData.value.title;
        item.icon = formData.value.icon;
        item.to = formData.value.to;
        item.componentPath = formData.value.componentPath;
        if (roleStrings.length > 0) {
            item.roles = roleStrings;
        } else {
            delete item.roles;
        }
    }
    displayEditDialog.value = false;
};

// -- Actions: Delete --
const deleteCategory = (index) => {
    if (confirm('¿Estás seguro de eliminar esta categoría entera?')) {
        menuData.value.splice(index, 1);
    }
};

const deleteItem = (catIndex, itemIndex) => {
    if (confirm('¿Estás seguro de eliminar este ítem del menú?')) {
        menuData.value[catIndex].items.splice(itemIndex, 1);
    }
};

// -- Actions: Add --
const addCategory = () => {
    menuData.value.push({ label: 'Nueva Categoría', icon: 'pi pi-folder', items: [] });
};

const addItem = (catIndex) => {
    if (!menuData.value[catIndex].items) menuData.value[catIndex].items = [];
    menuData.value[catIndex].items.push({
        label: 'Nuevo Ítem',
        title: 'Nuevo Ítem',
        icon: 'pi pi-file',
        to: '/nueva-ruta',
        componentPath: '/src/views/Dashboard.vue',
        roles: ['all']
    });
};

</script>

<template>
    <div class="grid">
        <div class="col-12">
            <div class="card">
                <div class="flex justify-content-between align-items-center mb-4">
                    <h5>Gestión de Menús</h5>
                    <div class="flex gap-2">
                        <Button label="Restaurar por Defecto" icon="pi pi-refresh" severity="secondary" outlined
                            @click="resetToDefault" />
                        <Button label="Guardar Configuración" icon="pi pi-save" @click="saveConfig" />
                    </div>
                </div>

                <div class="mb-4">
                    <p class="text-secondary">Arrastra o usa los botones para reordenar las categorías y páginas del
                        menú lateral. Requiere recargar la página para visualizar cambios globales. (Los cambios se
                        guardan localmente en el dispositivo actual temporalmente).</p>
                    <Button label="Agregar Categoría" icon="pi pi-plus" severity="success" class="mt-2"
                        @click="addCategory" />
                </div>

                <div class="flex flex-column gap-3">
                    <div v-for="(category, catIndex) in menuData" :key="catIndex"
                        class="border-1 surface-border border-round p-3 surface-ground">
                        <div class="flex justify-content-between align-items-center mb-3">
                            <div class="flex align-items-center gap-2 text-xl font-bold">
                                <i :class="category.icon"></i>
                                <span>{{ category.label }}</span>
                            </div>
                            <div class="flex gap-2">
                                <Button icon="pi pi-chevron-up" class="p-button-rounded p-button-text p-button-sm"
                                    @click="moveCategoryUp(catIndex)" :disabled="catIndex === 0" />
                                <Button icon="pi pi-chevron-down" class="p-button-rounded p-button-text p-button-sm"
                                    @click="moveCategoryDown(catIndex)" :disabled="catIndex === menuData.length - 1" />
                                <Button icon="pi pi-pencil"
                                    class="p-button-rounded p-button-outlined p-button-sm p-button-info"
                                    @click="openEditCategory(catIndex)" />
                                <Button icon="pi pi-trash"
                                    class="p-button-rounded p-button-outlined p-button-sm p-button-danger"
                                    @click="deleteCategory(catIndex)" />
                            </div>
                        </div>

                        <ul class="list-none p-0 m-0 border-top-1 surface-border py-2">
                            <li v-for="(item, itemIndex) in category.items" :key="itemIndex"
                                class="flex justify-content-between align-items-center p-2 hover:surface-hover border-round transition-colors transition-duration-150">
                                <div class="flex align-items-center gap-2">
                                    <i :class="item.icon" class="text-color-secondary"></i>
                                    <span>{{ item.label }}</span>
                                    <small class="text-color-secondary ml-3 bg-primary-reverse px-2 py-1 border-round"
                                        v-if="item.roles && item.roles.length > 0">{{ item.roles.join(', ') }}</small>
                                </div>
                                <div class="flex gap-2">
                                    <Button icon="pi pi-arrow-up" class="p-button-rounded p-button-text p-button-sm"
                                        @click="moveItemUp(catIndex, itemIndex)" :disabled="itemIndex === 0" />
                                    <Button icon="pi pi-arrow-down" class="p-button-rounded p-button-text p-button-sm"
                                        @click="moveItemDown(catIndex, itemIndex)"
                                        :disabled="itemIndex === category.items.length - 1" />
                                    <Button icon="pi pi-pencil"
                                        class="p-button-rounded p-button-text p-button-sm p-button-info"
                                        @click="openEditItem(catIndex, itemIndex)" />
                                    <Button icon="pi pi-trash"
                                        class="p-button-rounded p-button-text p-button-sm p-button-danger"
                                        @click="deleteItem(catIndex, itemIndex)" />
                                </div>
                            </li>
                        </ul>

                        <div class="mt-2 text-center">
                            <Button label="Agregar Ítem a esta categoría" icon="pi pi-plus" size="small" outlined
                                severity="success" @click="addItem(catIndex)" />
                        </div>
                    </div>
                </div>

                <!-- Modal Edit -->
                <Dialog v-model:visible="displayEditDialog" :style="{ width: '450px' }" header="Editar Propiedades"
                    :modal="true" class="p-fluid">
                    <div class="field">
                        <label for="label">Nombre (Label)</label>
                        <InputText id="label" v-model="formData.label" required autofocus />
                    </div>

                    <div class="field" v-if="editMode === 'item'">
                        <label for="title">Título de la Página (Title)</label>
                        <InputText id="title" v-model="formData.title" placeholder="Para la etiqueta del navegador" />
                    </div>

                    <div class="field">
                        <label for="icon">Ícono (PrimeIcons)</label>
                        <InputText id="icon" v-model="formData.icon" placeholder="pi pi-fw pi-home" />
                    </div>

                    <div class="field" v-if="editMode === 'item'">
                        <label for="to">Ruta Local (URL)</label>
                        <InputText id="to" v-model="formData.to" placeholder="/centro-servicios/x" />
                    </div>

                    <div class="field" v-if="editMode === 'item'">
                        <label for="componentPath">Ruta del Componente (.vue)</label>
                        <InputText id="componentPath" v-model="formData.componentPath"
                            placeholder="/src/views/...vue" />
                    </div>

                    <div class="field">
                        <label for="roles">Roles de Acceso (Déjalo vacío o usa 'all' para acceso público)</label>
                        <MultiSelect id="roles" v-model="formData.roles" :options="rolesList" optionLabel="name"
                            placeholder="Seleccionar Roles" :filter="true" display="chip" class="w-full"
                            :loading="isLoadingRoles" />
                    </div>

                    <template #footer>
                        <Button label="Cancelar" icon="pi pi-times" class="p-button-text"
                            @click="displayEditDialog = false" />
                        <Button label="Guardar Configuración Modal" icon="pi pi-check" @click="saveEdit" />
                    </template>
                </Dialog>

                <Toast />
            </div>
        </div>
    </div>
</template>

<style scoped>
.surface-hover:hover {
    background-color: var(--surface-hover);
}
</style>
