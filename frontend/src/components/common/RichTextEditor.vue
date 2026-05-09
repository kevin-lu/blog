<template>
  <div class="rich-text-editor">
    <div v-if="editor" class="toolbar">
      <n-space>
        <n-button
          size="small"
          :type="editor.isActive('bold') ? 'primary' : 'default'"
          @click="editor.chain().focus().toggleBold().run()"
        >
          <template #icon>
            <n-icon :component="Brush" />
          </template>
        </n-button>

        <n-button
          size="small"
          :type="editor.isActive('italic') ? 'primary' : 'default'"
          @click="editor.chain().focus().toggleItalic().run()"
        >
          <template #icon>
            <n-icon :component="Pencil" />
          </template>
        </n-button>

        <n-button
          size="small"
          :type="editor.isActive('underline') ? 'primary' : 'default'"
          @click="editor.chain().focus().toggleUnderline().run()"
        >
          <template #icon>
            <n-icon :component="Underline" />
          </template>
        </n-button>

        <n-button
          size="small"
          :type="editor.isActive('strike') ? 'primary' : 'default'"
          @click="editor.chain().focus().toggleStrike().run()"
        >
          <template #icon>
            <n-icon :component="Text" />
          </template>
        </n-button>

        <n-divider vertical />

        <n-button
          size="small"
          :type="editor.isActive('heading', { level: 1 }) ? 'primary' : 'default'"
          @click="editor.chain().focus().toggleHeading({ level: 1 }).run()"
        >
          H1
        </n-button>

        <n-button
          size="small"
          :type="editor.isActive('heading', { level: 2 }) ? 'primary' : 'default'"
          @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
        >
          H2
        </n-button>

        <n-button
          size="small"
          :type="editor.isActive('heading', { level: 3 }) ? 'primary' : 'default'"
          @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
        >
          H3
        </n-button>

        <n-divider vertical />

        <n-button
          size="small"
          :type="editor.isActive('bulletList') ? 'primary' : 'default'"
          @click="editor.chain().focus().toggleBulletList().run()"
        >
          <template #icon>
            <n-icon :component="List" />
          </template>
        </n-button>

        <n-button
          size="small"
          :type="editor.isActive('orderedList') ? 'primary' : 'default'"
          @click="editor.chain().focus().toggleOrderedList().run()"
        >
          <template #icon>
            <n-icon :component="ListOutline" />
          </template>
        </n-button>

        <n-button
          size="small"
          :type="editor.isActive('blockquote') ? 'primary' : 'default'"
          @click="editor.chain().focus().toggleBlockquote().run()"
        >
          <template #icon>
            <n-icon :component="TextOutline" />
          </template>
        </n-button>

        <n-button
          size="small"
          :type="editor.isActive('codeBlock') ? 'primary' : 'default'"
          @click="editor.chain().focus().toggleCodeBlock().run()"
        >
          <template #icon>
            <n-icon :component="CodeSlash" />
          </template>
        </n-button>

        <n-divider vertical />

        <n-button
          size="small"
          @click="handleAddImage"
        >
          <template #icon>
            <n-icon :component="ImageOutline" />
          </template>
        </n-button>

        <n-button
          size="small"
          :type="editor.isActive('link') ? 'primary' : 'default'"
          @click="handleAddLink"
        >
          <template #icon>
            <n-icon :component="LinkOutline" />
          </template>
        </n-button>

        <n-divider vertical />

        <n-button
          size="small"
          @click="editor.chain().focus().unsetAllMarks().run()"
        >
          清除格式
        </n-button>
      </n-space>
    </div>

    <div class="editor-container">
      <editor-content :editor="editor" class="editor-content" />
    </div>

    <!-- Image Upload Dialog -->
    <n-modal
      v-model:show="showImageModal"
      preset="dialog"
      title="插入图片"
    >
      <n-space vertical>
        <n-upload
          :action="uploadUrl"
          :headers="uploadHeaders"
          :show-file-list="false"
          @finish="handleImageUploadFinish"
        >
          <n-button block>
            <template #icon>
              <n-icon :component="CloudUploadOutline" />
            </template>
            上传图片
          </n-button>
        </n-upload>

        <n-input
          v-model:value="imageUrl"
          placeholder="或输入图片 URL"
        >
          <template #suffix>
            <n-button text type="primary" @click="insertImage(imageUrl)">
              插入
            </n-button>
          </template>
        </n-input>
      </n-space>
    </n-modal>

    <!-- Link Dialog -->
    <n-modal
      v-model:show="showLinkModal"
      preset="dialog"
      title="插入链接"
    >
      <n-space vertical>
        <n-input
          v-model:value="linkUrl"
          placeholder="输入链接地址"
        />
        <n-input
          v-model:value="linkText"
          placeholder="链接文本（可选）"
        />
      </n-space>
      <template #action>
        <n-space justify="end">
          <n-button @click="showLinkModal = false">
            取消
          </n-button>
          <n-button type="primary" @click="insertLink">
            插入
          </n-button>
          <n-button
            v-if="editor?.isActive('link')"
            type="error"
            @click="removeLink"
          >
            移除链接
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onBeforeUnmount, computed } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import Placeholder from '@tiptap/extension-placeholder'
import Underline from '@tiptap/extension-underline'
import TextAlign from '@tiptap/extension-text-align'
import Highlight from '@tiptap/extension-highlight'
import Typography from '@tiptap/extension-typography'
import {
  Brush,
  Pencil,
  List,
  ListOutline,
  CodeSlash,
  ImageOutline,
  LinkOutline,
  CloudUploadOutline,
  Text,
  TextOutline,
} from '@vicons/ionicons5'
import { useMessage } from 'naive-ui'
import { uploadApi } from '@/api'

interface Props {
  modelValue: string
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请输入内容...',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const message = useMessage()

const showImageModal = ref(false)
const showLinkModal = ref(false)
const imageUrl = ref('')
const linkUrl = ref('')
const linkText = ref('')

// 上传配置
const uploadUrl = computed(() => {
  const baseURL = (import.meta as any).env.VITE_API_BASE_URL || '/api'
  return `${baseURL}/upload`
})

const uploadHeaders = computed(() => {
  const token = localStorage.getItem('access_token')
  return {
    Authorization: token ? `Bearer ${token}` : '',
  }
})

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit,
    Image.configure({
      HTMLAttributes: {
        class: 'image',
      },
    }),
    Link.configure({
      openOnClick: false,
      HTMLAttributes: {
        class: 'link',
      },
    }),
    Placeholder.configure({
      placeholder: props.placeholder,
    }),
    Underline,
    TextAlign.configure({
      types: ['heading', 'paragraph'],
    }),
    Highlight,
    Typography,
  ],
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  },
})

watch(
  () => props.modelValue,
  (value) => {
    const isSame = editor.value?.getHTML() === value
    if (!isSame && editor.value) {
      editor.value.commands.setContent(value)
    }
  }
)

onBeforeUnmount(() => {
  editor.value?.destroy()
})

const handleAddImage = () => {
  imageUrl.value = ''
  showImageModal.value = true
}

const handleImageUploadFinish = ({ file, event }: any) => {
  try {
    const response = JSON.parse(event.target.responseText)
    if (response.data && response.data.url) {
      insertImage(response.data.url)
      message.success('图片上传成功')
    }
  } catch (error) {
    message.error('图片上传失败')
  }
  showImageModal.value = false
}

const insertImage = (url: string) => {
  if (url && editor.value) {
    editor.value.chain().focus().setImage({ src: url }).run()
    showImageModal.value = false
  }
}

const handleAddLink = () => {
  linkUrl.value = ''
  linkText.value = ''
  showLinkModal.value = true
}

const insertLink = () => {
  if (linkUrl.value && editor.value) {
    editor.value
      .chain()
      .focus()
      .extendMarkRange('link')
      .setLink({ href: linkUrl.value })
      .run()
    showLinkModal.value = false
  }
}

const removeLink = () => {
  if (editor.value) {
    editor.value.chain().focus().unsetLink().run()
    showLinkModal.value = false
  }
}
</script>

<style scoped>
.rich-text-editor {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.toolbar {
  padding: 8px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  overflow-x: auto;
}

.toolbar .n-divider {
  margin: 0 4px;
}

.editor-container {
  background: white;
}

.editor-content {
  padding: 16px;
  min-height: 400px;
  max-height: 800px;
  overflow-y: auto;
}

:deep(.ProseMirror) {
  outline: none;
  min-height: 380px;
}

:deep(.ProseMirror p.is-editor-empty:first-child::before) {
  color: #adb5bd;
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}

:deep(.ProseMirror h1),
:deep(.ProseMirror h2),
:deep(.ProseMirror h3) {
  margin-top: 1em;
  margin-bottom: 0.5em;
  line-height: 1.3;
}

:deep(.ProseMirror p) {
  margin-top: 0.75em;
  margin-bottom: 0.75em;
}

:deep(.ProseMirror ul),
:deep(.ProseMirror ol) {
  padding-left: 1.5em;
  margin-top: 0.75em;
  margin-bottom: 0.75em;
}

:deep(.ProseMirror blockquote) {
  border-left: 3px solid #e0e0e0;
  padding-left: 1em;
  margin-left: 0;
  margin-right: 0;
  font-style: italic;
  color: #666;
}

:deep(.ProseMirror pre) {
  background: #f5f5f5;
  border-radius: 4px;
  padding: 1em;
  overflow-x: auto;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

:deep(.ProseMirror code) {
  background: #f5f5f5;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

:deep(.ProseMirror img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 1em auto;
  border-radius: 4px;
}

:deep(.ProseMirror a.link) {
  color: #18a058;
  text-decoration: underline;
}
</style>
