<script setup lang="ts">
import {LayoutDashboard,ClipboardList,Users,UserRound,Menu,X,ChevronDown,LogOut,Plus,ListTodo,CircleAlert,LoaderCircle,Check,Clock,Paperclip,Search,Bell,ArrowRight,Pencil,Trash2,Activity,ShieldCheck,Sun,Moon,Folder,Eye,EyeOff} from 'lucide-vue-next'
const props=withDefaults(defineProps<{name:string;size?:number|string;strokeWidth?:number}>(),{size:20,strokeWidth:1.8})
const icons={dashboard:LayoutDashboard,requests:ClipboardList,users:Users,user:UserRound,menu:Menu,close:X,chevronDown:ChevronDown,logout:LogOut,plus:Plus,total:ListTodo,open:CircleAlert,progress:LoaderCircle,check:Check,clock:Clock,paperclip:Paperclip,search:Search,bell:Bell,arrowRight:ArrowRight,edit:Pencil,trash:Trash2,activity:Activity,shield:ShieldCheck,sun:Sun,moon:Moon,folder:Folder,eye:Eye,eyeOff:EyeOff}
const current=computed(()=>icons[props.name as keyof typeof icons]??Folder)
</script><template><component :is="current" :size="props.size" :stroke-width="props.strokeWidth" aria-hidden="true"/></template>
