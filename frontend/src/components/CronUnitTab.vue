<template>
  <div class="cron-unit-tab pa-2">
    <v-radio-group v-model="type" hide-details>

      <v-radio class="mb-2" value="every">
        <template #label>
          <span class="text-body-2">每{{ label }} ( * )</span>
        </template>
      </v-radio>

      <v-radio class="mb-2" value="interval">
        <template #label>
          <div class="d-flex align-center flex-wrap">
            <span class="text-body-2 mr-2">从第</span>
            <v-number-input
                v-model="intervalStart"
                :max="max" :min="min"
                control-variant="split"
                density="compact"
                hide-details
                style="width: 150px"
                variant="outlined"
                @focus="type = 'interval'"
            ></v-number-input>
            <span class="text-body-2 mx-2">{{ label }}开始，每隔</span>
            <v-number-input
                v-model="intervalStep"
                :max="max" :min="1"
                control-variant="split"
                density="compact"
                hide-details
                style="width: 150px"
                variant="outlined"
                @focus="type = 'interval'"
            ></v-number-input>
            <span class="text-body-2 ml-2">{{ label }}执行一次</span>
          </div>
        </template>
      </v-radio>

      <v-radio class="mb-2" value="range">
        <template #label>
          <div class="d-flex align-center flex-wrap">
            <span class="text-body-2 mr-2">周期从</span>
            <v-number-input
                v-model="rangeStart"
                :max="max" :min="min"
                density="compact"
                hide-details
                style="width: 150px"
                variant="outlined"
                @focus="type = 'range'"
            ></v-number-input>
            <span class="text-body-2 mx-2">-</span>
            <v-number-input
                v-model="rangeEnd"
                :max="max" :min="min"
                density="compact"
                hide-details
                style="width: 150px"
                variant="outlined"
                @focus="type = 'range'"
            ></v-number-input>
            <span class="text-body-2 ml-2">{{ label }}</span>
          </div>
        </template>
      </v-radio>

      <v-radio class="mb-2" value="specific">
        <template #label>
          <span class="text-body-2">指定具体{{ label }}</span>
        </template>
      </v-radio>
    </v-radio-group>

    <v-expand-transition>
      <div v-if="type === 'specific'" class="bg-surface-variant rounded-lg pa-3 ml-8">
        <v-row dense>
          <v-col v-for="n in (max - min + 1)" :key="n" class="pa-0 ma-1" cols="auto">
            <v-chip
                :color="selected.includes(n + min - 1) ? 'primary' : undefined"
                :variant="selected.includes(n + min - 1) ? 'flat' : 'outlined'"
                link
                size="small"
                @click="toggleSpecific(n + min - 1)"
            >
              {{ n + min - 1 }}
            </v-chip>
          </v-col>
        </v-row>
      </div>
    </v-expand-transition>
  </div>
</template>

<script setup>
import {computed, ref, watch} from 'vue'

const props = defineProps(['modelValue', 'label', 'min', 'max'])
const emit = defineEmits(['update:modelValue'])

const type = ref('every')
const intervalStart = ref(props.min)
const intervalStep = ref(1)
const rangeStart = ref(props.min)
const rangeEnd = ref(props.min + 1)
const selected = ref([])

// 生成Cron片段
const result = computed(() => {
  switch (type.value) {
    case 'every':
      return '*'
    case 'interval':
      return `${intervalStart.value}/${intervalStep.value}`
    case 'range':
      return `${rangeStart.value}-${rangeEnd.value}`
    case 'specific':
      return selected.value.length > 0
          ? selected.value.sort((a, b) => a - b).join(',')
          : '*'
    default:
      return '*'
  }
})

watch(result, (val) => {
  emit('update:modelValue', val)
})

const toggleSpecific = (val) => {
  type.value = 'specific'
  const idx = selected.value.indexOf(val)
  if (idx === -1) selected.value.push(val)
  else selected.value.splice(idx, 1)
}

</script>

<style scoped>
.v-input--density-compact {
  --v-input-control-height: 32px;
}
</style>