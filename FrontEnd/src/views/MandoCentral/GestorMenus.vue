<script setup>
import { ref, onMounted } from 'vue';
import { fetchRoles } from '@/service/api';
import defaultMenuData from '@/config/menu.json';
import primeIconsJson from '@/config/primeicons.json';
import { useToast } from 'primevue/usetoast';

const toast = useToast();
const menuData = ref([]);
const rolesList = ref([]);

// Edit state
const editMode = ref(''); // 'category' or 'item'
const editingCategoryIndex = ref(-1);
const editingItemIndex = ref(-1);
const formData = ref({});

// Icon autocomplete state
const filteredIcons = ref([]);

// Load data on mount
onMounted(async () => {
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

    try {
        const response = await fetchRoles();
        if (response.success && response.data) {
            rolesList.value = response.data.map(r => ({ name: r.nombre, code: r.nombre }));
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los roles', life: 3000 });
        }
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Fallo al conectar con el servidor', life: 3000 });
    }

    if (menuData.value.length > 0) {
        selectCategory(0);
    }
});

// -- Actions: Main Config --
const saveConfig = () => {
    localStorage.setItem('nexusMenuConfig', JSON.stringify(menuData.value));
    toast.add({ severity: 'success', summary: 'Éxito', detail: 'Configuración guardada. Recarga el navegador para observar los cambios en el menú global.', life: 4000 });
};

const resetToDefault = () => {
    localStorage.removeItem('nexusMenuConfig');
    menuData.value = JSON.parse(JSON.stringify(defaultMenuData));
    editMode.value = '';
    toast.add({ severity: 'info', summary: 'Restaurado', detail: 'Se ha restaurado el menú por defecto.', life: 3000 });
};

// -- Actions: Select to Edit --
const selectCategory = (catIndex) => {
    editMode.value = 'category';
    editingCategoryIndex.value = catIndex;
    editingItemIndex.value = -1;
    const cat = menuData.value[catIndex];

    // PickList requires [source, target] arrays
    const assignedRoleStrings = cat.roles || [];
    const targetRoles = rolesList.value.filter(r => assignedRoleStrings.includes(r.code));
    const sourceRoles = rolesList.value.filter(r => !assignedRoleStrings.includes(r.code));

    formData.value = {
        label: cat.label,
        icon: cat.icon,
        roles: [sourceRoles, targetRoles]
    };
};

const selectItem = (catIndex, itemIndex) => {
    editMode.value = 'item';
    editingCategoryIndex.value = catIndex;
    editingItemIndex.value = itemIndex;
    const item = menuData.value[catIndex].items[itemIndex];

    // PickList requires [source, target] arrays
    const assignedRoleStrings = item.roles || [];
    const targetRoles = rolesList.value.filter(r => assignedRoleStrings.includes(r.code));
    const sourceRoles = rolesList.value.filter(r => !assignedRoleStrings.includes(r.code));

    formData.value = {
        label: item.label,
        title: item.title || item.label,
        icon: item.icon,
        to: item.to,
        componentPath: item.componentPath,
        roles: [sourceRoles, targetRoles]
    };
};

// -- Actions: Reorder Categories --
const moveCategoryUp = (index) => {
    if (index > 0) {
        const temp = menuData.value[index];
        menuData.value[index] = menuData.value[index - 1];
        menuData.value[index - 1] = temp;
        // Keep selection synced
        if (editingCategoryIndex.value === index) editingCategoryIndex.value--;
        else if (editingCategoryIndex.value === index - 1) editingCategoryIndex.value++;
    }
};

const moveCategoryDown = (index) => {
    if (index < menuData.value.length - 1) {
        const temp = menuData.value[index];
        menuData.value[index] = menuData.value[index + 1];
        menuData.value[index + 1] = temp;
        if (editingCategoryIndex.value === index) editingCategoryIndex.value++;
        else if (editingCategoryIndex.value === index + 1) editingCategoryIndex.value--;
    }
};

// -- Actions: Reorder Items --
const moveItemUp = (catIndex, itemIndex) => {
    const items = menuData.value[catIndex].items;
    if (itemIndex > 0) {
        const temp = items[itemIndex];
        items[itemIndex] = items[itemIndex - 1];
        items[itemIndex - 1] = temp;
        if (editingCategoryIndex.value === catIndex && editingItemIndex.value === itemIndex) editingItemIndex.value--;
        else if (editingCategoryIndex.value === catIndex && editingItemIndex.value === itemIndex - 1) editingItemIndex.value++;
    }
};

const moveItemDown = (catIndex, itemIndex) => {
    const items = menuData.value[catIndex].items;
    if (itemIndex < items.length - 1) {
        const temp = items[itemIndex];
        items[itemIndex] = items[itemIndex + 1];
        items[itemIndex + 1] = temp;
        if (editingCategoryIndex.value === catIndex && editingItemIndex.value === itemIndex) editingItemIndex.value++;
        else if (editingCategoryIndex.value === catIndex && editingItemIndex.value === itemIndex + 1) editingItemIndex.value--;
    }
};

// -- Actions: Add / Delete --
const addCategory = () => {
    menuData.value.push({ label: 'Nueva Categoría', icon: 'pi pi-folder', items: [] });
    selectCategory(menuData.value.length - 1);
};

const deleteCategory = (index) => {
    if (confirm('¿Estás seguro de eliminar esta categoría entera?')) {
        menuData.value.splice(index, 1);
        editMode.value = '';
    }
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
    selectItem(catIndex, menuData.value[catIndex].items.length - 1);
};

const deleteItem = (catIndex, itemIndex) => {
    if (confirm('¿Estás seguro de eliminar este ítem?')) {
        menuData.value[catIndex].items.splice(itemIndex, 1);
        editMode.value = '';
    }
};

// -- Save form data to in-memory model --
const applyEdit = () => {
    // PickList stores selected items in index 1
    const roleStrings = (formData.value.roles && formData.value.roles[1]) ? formData.value.roles[1].map(r => r.code) : [];

    // Normalize icon value from autocomplete
    let iconValue = formData.value.icon;
    if (iconValue && !iconValue.startsWith('pi pi-')) {
        if (iconValue.startsWith('pi-')) {
            iconValue = 'pi ' + iconValue;
        } else {
            iconValue = 'pi pi-' + iconValue;
        }
    }

    if (editMode.value === 'category') {
        const cat = menuData.value[editingCategoryIndex.value];
        cat.label = formData.value.label;
        cat.icon = iconValue;
        if (roleStrings.length > 0) cat.roles = roleStrings;
        else delete cat.roles;

        // Update form data so we instantly see what was set
        formData.value.icon = iconValue;
    } else if (editMode.value === 'item') {
        const item = menuData.value[editingCategoryIndex.value].items[editingItemIndex.value];
        item.label = formData.value.label;
        item.title = formData.value.title;
        item.icon = iconValue;
        item.to = formData.value.to;
        item.componentPath = formData.value.componentPath;
        if (roleStrings.length > 0) item.roles = roleStrings;
        else delete item.roles;

        formData.value.icon = iconValue;
    }
    toast.add({ severity: 'success', summary: 'Aplicado', detail: 'Cambios aplicados localmente.', life: 2000 });
};

const searchIcon = (event) => {
    let query = event.query.toLowerCase().trim();
    if (query.startsWith('pi pi-')) query = query.replace('pi pi-', '');
    else if (query.startsWith('pi-')) query = query.replace('pi-', '');

    if (!query) {
        filteredIcons.value = primeIconsJson.slice(0, 50); // Show max 50 default
    } else {
        filteredIcons.value = primeIconsJson.filter(icon => icon.includes(query)).slice(0, 50);
    }
};

</script>

<template>
    <div class="card">
        <div class="flex flex-column md:flex-row justify-content-between align-items-center mb-4 gap-3">
            <div>
                <h4 class="m-0">Gestión de Menús</h4>
                <p class="m-0 text-color-secondary">Configura el menú lateral de forma visual.</p>
            </div>
            <div class="flex gap-2">
                <Button label="Añadir Categoría Principal" icon="pi pi-plus" severity="success" outlined
                    @click="addCategory" />
                <Button label="Restaurar Defecto" icon="pi pi-refresh" severity="secondary" outlined
                    @click="resetToDefault" />
                <Button label="Guardar Configuración Global" icon="pi pi-save" @click="saveConfig" />
            </div>
        </div>

        <div class="grid mt-4">
            <!-- Left Panel: Sidebar-like Menu Tree -->
            <div class="col-12 xl:col-4 lg:col-4 md:col-5">
                <div class="card h-full p-0 flex flex-column shadow-1 border-1 surface-border">
                    <div class="flex-grow-1 overflow-y-auto w-full p-3 mt-3" style="max-height: 60vh;">
                        <ul class="list-none p-0 m-0">
                            <li v-for="(category, catIndex) in menuData" :key="catIndex" class="mb-2">
                                <!-- Category Item -->
                                <div class="flex align-items-center justify-content-between p-3 border-round cursor-pointer transition-colors"
                                    :class="{ 'surface-100 font-bold border-left-3 border-primary text-primary': editMode === 'category' && editingCategoryIndex === catIndex, 'surface-50 text-color': !(editMode === 'category' && editingCategoryIndex === catIndex) }"
                                    @click="selectCategory(catIndex)">
                                    <div class="flex align-items-center gap-2">
                                        <i :class="category.icon"></i>
                                        <span class="font-semibold">{{ category.label }}</span>
                                    </div>
                                    <Button icon="pi pi-plus"
                                        class="p-button-rounded p-button-text p-button-sm p-0 m-0 w-2rem h-2rem p-button-success"
                                        @click.stop="addItem(catIndex)" v-tooltip.top="'Añadir Sub-ítem'" />
                                </div>

                                <!-- Sub Items List -->
                                <ul class="list-none p-0 m-0 pl-3 mt-2"
                                    v-if="category.items && category.items.length > 0">
                                    <li v-for="(item, itemIndex) in category.items" :key="itemIndex" class="mb-1">
                                        <div class="flex align-items-center p-2 border-round cursor-pointer transition-colors"
                                            :class="{ 'surface-200 font-bold text-primary border-left-3 border-primary': editMode === 'item' && editingCategoryIndex === catIndex && editingItemIndex === itemIndex, 'hover:surface-100 text-color-secondary': !(editMode === 'item' && editingCategoryIndex === catIndex && editingItemIndex === itemIndex) }"
                                            @click.stop="selectItem(catIndex, itemIndex)">
                                            <i :class="[item.icon, 'mr-2 text-sm']"></i>
                                            <span class="text-sm">{{ item.label }}</span>
                                        </div>
                                    </li>
                                </ul>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Right Panel: Edit Form -->
            <div class="col-12 xl:col-8 lg:col-8 md:col-7">
                <div class="card h-full surface-ground border-1 surface-border shadow-1" v-if="editMode !== ''">

                    <!-- Header with Actions -->
                    <div
                        class="flex align-items-center justify-content-between mb-4 border-bottom-1 surface-border pb-3">
                        <h5 class="m-0 flex align-items-center gap-2">
                            <i :class="formData.icon" class="text-xl text-primary"></i>
                            Editando {{ editMode === 'category' ? 'Categoría' : 'Ítem' }}: <span class="text-primary">{{
                                formData.label }}</span>
                        </h5>

                        <div class="flex gap-2" v-if="editMode === 'category'">
                            <Button icon="pi pi-arrow-up" class="p-button-outlined p-button-sm p-button-secondary"
                                @click="moveCategoryUp(editingCategoryIndex)" :disabled="editingCategoryIndex === 0"
                                v-tooltip.top="'Subir Posición'" />
                            <Button icon="pi pi-arrow-down" class="p-button-outlined p-button-sm p-button-secondary"
                                @click="moveCategoryDown(editingCategoryIndex)"
                                :disabled="editingCategoryIndex === menuData.length - 1"
                                v-tooltip.top="'Bajar Posición'" />
                            <Button icon="pi pi-trash" class="p-button-danger p-button-outlined p-button-sm"
                                @click="deleteCategory(editingCategoryIndex)" v-tooltip.top="'Eliminar'" />
                        </div>
                        <div class="flex gap-2" v-if="editMode === 'item'">
                            <Button icon="pi pi-arrow-up" class="p-button-outlined p-button-sm p-button-secondary"
                                @click="moveItemUp(editingCategoryIndex, editingItemIndex)"
                                :disabled="editingItemIndex === 0" v-tooltip.top="'Subir Posición'" />
                            <Button icon="pi pi-arrow-down" class="p-button-outlined p-button-sm p-button-secondary"
                                @click="moveItemDown(editingCategoryIndex, editingItemIndex)"
                                :disabled="editingItemIndex === menuData[editingCategoryIndex].items.length - 1"
                                v-tooltip.top="'Bajar Posición'" />
                            <Button icon="pi pi-trash" class="p-button-danger p-button-outlined p-button-sm"
                                @click="deleteItem(editingCategoryIndex, editingItemIndex)"
                                v-tooltip.top="'Eliminar'" />
                        </div>
                    </div>

                    <div class="p-fluid">
                        <div class="grid">
                            <div class="col-12 md:col-6">
                                <div class="field mb-4">
                                    <label for="label" class="font-bold">Nombre en el Menú (Label)</label>
                                    <InputText id="label" v-model="formData.label" required autofocus
                                        placeholder="Ej. Centro de Servicios" />
                                </div>
                            </div>
                            <div class="col-12 md:col-6">
                                <div class="field mb-4">
                                    <label for="icon" class="font-bold">Ícono (Buscar)</label>
                                    <div class="p-inputgroup">
                                        <span class="p-inputgroup-addon">
                                            <i :class="formData.icon"></i>
                                        </span>
                                        <AutoComplete inputId="icon" v-model="formData.icon"
                                            :suggestions="filteredIcons" @complete="searchIcon" dropdown
                                            placeholder="Busca un icono ej. pi-home">
                                            <template #option="slotProps">
                                                <div class="flex align-items-center gap-2">
                                                    <i :class="'pi ' + slotProps.option"
                                                        style="font-size: 1.25rem; width: 2rem; text-align: center"></i>
                                                    <div>pi {{ slotProps.option }}</div>
                                                </div>
                                            </template>
                                        </AutoComplete>
                                    </div>
                                    <small class="text-color-secondary">Puedes escribir o borrar para ver la
                                        lista.</small>
                                </div>
                            </div>
                        </div>

                        <div class="field mb-4" v-if="editMode === 'item'">
                            <label for="title" class="font-bold">Título de la Página (Title)</label>
                            <InputText id="title" v-model="formData.title"
                                placeholder="Aparece en la pestaña del navegador" />
                            <small class="text-color-secondary">Nombre que se mostrará en las pestañas del explorador de
                                internet.</small>
                        </div>

                        <div class="grid" v-if="editMode === 'item'">
                            <div class="col-12 md:col-6">
                                <div class="field mb-4">
                                    <label for="to" class="font-bold">Ruta Local (to URL)</label>
                                    <InputText id="to" v-model="formData.to" placeholder="/centro-servicios/ruta" />
                                </div>
                            </div>
                            <div class="col-12 md:col-6">
                                <div class="field mb-4">
                                    <label for="componentPath" class="font-bold">Componente Físico (.vue)</label>
                                    <InputText id="componentPath" v-model="formData.componentPath"
                                        placeholder="/src/views/...vue" />
                                    <small class="text-color-secondary">Ruta exacta del componente. Importante mantener
                                        la
                                        capitalización.</small>
                                </div>
                            </div>
                        </div>

                        <div class="field mb-4">
                            <span class="font-bold block mb-2">Roles Restringidos a la Sección</span>
                            <PickList v-model="formData.roles" dataKey="code" breakpoint="768px"
                                listStyle="height: 400px; min-height: 400px" :showSourceControls="false"
                                :showTargetControls="false">
                                <template #sourceheader> Disponibles </template>
                                <template #targetheader> Asignados </template>
                                <template #item="slotProps">
                                    <div class="flex align-items-center gap-2 text-sm p-1">
                                        <i class="pi pi-user text-primary"></i>
                                        <span>{{ slotProps.item.name }}</span>
                                    </div>
                                </template>
                            </PickList>
                            <small class="text-color-secondary mt-2 block">Si "Asignados" está vacío, cualquier usuario
                                autenticado tendrá
                                acceso público a la sección.</small>
                        </div>

                        <div class="flex justify-content-end mt-4 pt-4 border-top-1 surface-border">
                            <Button label="Aplicar Cambios" icon="pi pi-check" size="large" @click="applyEdit"
                                severity="success" />
                        </div>
                    </div>
                </div>

                <div class="card h-full flex flex-column align-items-center justify-content-center text-center surface-ground border-1 surface-border border-dashed p-6"
                    v-else>
                    <i class="pi pi-pen-to-square text-6xl text-color-secondary mb-3"></i>
                    <h5 class="text-color-secondary m-0 mb-2">Panel del Editor</h5>
                    <p class="text-color-secondary m-0 max-w-sm">Selecciona una categoría o un ítem en el árbol
                        interactivo de la
                        izquierda para comenzar a editar su comportamiento.</p>
                </div>
            </div>
        </div>

        <Toast />
    </div>
</template>

<style scoped>
.surface-hover:hover {
    background-color: var(--surface-hover) !important;
}

/* Scrollbar styling for the menu tree */
.overflow-y-auto::-webkit-scrollbar {
    width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
    background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
    background: var(--surface-border);
    border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
    background: var(--text-color-secondary);
}
</style>
