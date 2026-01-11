import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';

interface CreateProjectProps {
  aiModel: string;
  language: string;
}

const CreateProject = ({ aiModel, language }: CreateProjectProps) => {
  const [projectType, setProjectType] = useState('website');
  const [description, setDescription] = useState('');
  const [projectName, setProjectName] = useState('');
  const [technologies, setTechnologies] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const projectTypes = [
    { value: 'website', label: 'Веб-сайт', icon: 'Globe', color: 'bg-blue-500' },
    { value: 'mobile', label: 'Мобильное приложение', icon: 'Smartphone', color: 'bg-purple-500' },
    { value: 'ai-tool', label: 'AI инструмент', icon: 'Brain', color: 'bg-pink-500' },
    { value: 'ai-webapp', label: 'AI веб-приложение', icon: 'Sparkles', color: 'bg-orange-500' },
  ];

  const techStacks = {
    website: ['React', 'Vue.js', 'Angular', 'Next.js', 'Tailwind CSS', 'TypeScript'],
    mobile: ['React Native', 'Flutter', 'Swift', 'Kotlin', 'Expo'],
    'ai-tool': ['Python', 'TensorFlow', 'PyTorch', 'scikit-learn', 'Pandas', 'NumPy'],
    'ai-webapp': ['React', 'Python', 'FastAPI', 'OpenAI API', 'LangChain', 'Transformers'],
  };

  const templates = [
    { name: 'Лендинг с CTA', desc: 'Одностраничный сайт с формой захвата', type: 'website' },
    { name: 'E-commerce', desc: 'Интернет-магазин с корзиной', type: 'website' },
    { name: 'Чат-приложение', desc: 'Мобильный мессенджер', type: 'mobile' },
    { name: 'AI Ассистент', desc: 'Chatbot с GPT интеграцией', type: 'ai-webapp' },
  ];

  const handleGenerate = () => {
    setIsGenerating(true);
    setTimeout(() => setIsGenerating(false), 3000);
  };

  const toggleTech = (tech: string) => {
    setTechnologies(prev =>
      prev.includes(tech) ? prev.filter(t => t !== tech) : [...prev, tech]
    );
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Icon name="Rocket" size={20} />
              Новый проект
            </CardTitle>
            <CardDescription>
              Опишите проект — агент сгенерирует полную структуру и код
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Название проекта</Label>
              <Input
                placeholder="Мой крутой проект"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
              />
            </div>

            <div>
              <Label>Тип проекта</Label>
              <div className="grid grid-cols-2 gap-3 mt-2">
                {projectTypes.map((type) => (
                  <Card
                    key={type.value}
                    className={`cursor-pointer transition-all hover:scale-105 ${
                      projectType === type.value ? 'ring-2 ring-primary' : ''
                    }`}
                    onClick={() => setProjectType(type.value)}
                  >
                    <CardContent className="pt-4 pb-3">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-lg ${type.color} flex items-center justify-center`}>
                          <Icon name={type.icon} className="text-white" size={20} />
                        </div>
                        <span className="font-medium text-sm">{type.label}</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            <div>
              <Label>Описание проекта</Label>
              <Textarea
                placeholder="Опишите функционал, дизайн, целевую аудиторию и другие требования..."
                className="min-h-32 mt-2"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <div>
              <Label>Технологии</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {techStacks[projectType as keyof typeof techStacks].map((tech) => (
                  <Badge
                    key={tech}
                    variant={technologies.includes(tech) ? 'default' : 'outline'}
                    className="cursor-pointer hover:scale-105 transition-transform"
                    onClick={() => toggleTech(tech)}
                  >
                    {tech}
                  </Badge>
                ))}
              </div>
            </div>

            <Button
              className="w-full"
              size="lg"
              onClick={handleGenerate}
              disabled={isGenerating || !projectName || !description}
            >
              {isGenerating ? (
                <>
                  <Icon name="Loader2" className="animate-spin mr-2" size={18} />
                  Генерация проекта...
                </>
              ) : (
                <>
                  <Icon name="Sparkles" className="mr-2" size={18} />
                  Создать проект
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="Zap" size={18} />
              Шаблоны проектов
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {templates.map((template, idx) => (
              <Card
                key={idx}
                className="cursor-pointer hover:bg-accent transition-colors"
                onClick={() => {
                  setProjectType(template.type);
                  setDescription(template.desc);
                  setProjectName(template.name);
                }}
              >
                <CardContent className="pt-3 pb-3">
                  <p className="font-medium text-sm">{template.name}</p>
                  <p className="text-xs text-muted-foreground mt-1">{template.desc}</p>
                </CardContent>
              </Card>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="Shield" size={18} />
              Безопасность
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-2">
                <Icon name="Check" className="text-green-500 mt-0.5" size={16} />
                <span>Защита от SQL-инъекций</span>
              </div>
              <div className="flex items-start gap-2">
                <Icon name="Check" className="text-green-500 mt-0.5" size={16} />
                <span>XSS/CSRF защита</span>
              </div>
              <div className="flex items-start gap-2">
                <Icon name="Check" className="text-green-500 mt-0.5" size={16} />
                <span>HTTPS по умолчанию</span>
              </div>
              <div className="flex items-start gap-2">
                <Icon name="Check" className="text-green-500 mt-0.5" size={16} />
                <span>Шифрование данных</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default CreateProject;
