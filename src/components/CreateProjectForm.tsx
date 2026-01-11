import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';
import { api } from '@/lib/api';
import { createOpenRouterClient } from '@/lib/openrouter';
import { useToast } from '@/hooks/use-toast';

interface CreateProjectFormProps {
  aiModel: string;
  language: string;
}

const CreateProjectForm = ({ aiModel, language }: CreateProjectFormProps) => {
  const [projectName, setProjectName] = useState('');
  const [description, setDescription] = useState('');
  const [projectType, setProjectType] = useState<'website' | 'mobile' | 'ai-tool' | 'ai-webapp'>('website');
  const [technologies, setTechnologies] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');
  const { toast } = useToast();

  const projectTypes = [
    { value: 'website' as const, label: 'Веб-сайт', icon: 'Globe', color: 'bg-blue-500' },
    { value: 'mobile' as const, label: 'Мобильное приложение', icon: 'Smartphone', color: 'bg-purple-500' },
    { value: 'ai-tool' as const, label: 'AI инструмент', icon: 'Brain', color: 'bg-pink-500' },
    { value: 'ai-webapp' as const, label: 'AI веб-приложение', icon: 'Sparkles', color: 'bg-orange-500' },
  ];

  const techStacks = {
    website: ['React', 'Vue.js', 'Next.js', 'TypeScript', 'Tailwind CSS'],
    mobile: ['React Native', 'Flutter', 'Swift', 'Kotlin'],
    'ai-tool': ['Python', 'TensorFlow', 'PyTorch', 'scikit-learn', 'Pandas'],
    'ai-webapp': ['React', 'Python', 'FastAPI', 'OpenAI API', 'LangChain'],
  };

  const templates = [
    { name: 'Landing Page', desc: 'Одностраничный сайт с формой', type: 'website' as const },
    { name: 'Dashboard', desc: 'Админ панель с графиками', type: 'website' as const },
    { name: 'Mobile Chat', desc: 'Мобильный мессенджер', type: 'mobile' as const },
    { name: 'AI Chatbot', desc: 'Бот с GPT интеграцией', type: 'ai-webapp' as const },
  ];

  const toggleTech = (tech: string) => {
    setTechnologies(prev =>
      prev.includes(tech) ? prev.filter(t => t !== tech) : [...prev, tech]
    );
  };

  const loadTemplate = (template: typeof templates[0]) => {
    setProjectType(template.type);
    setProjectName(template.name);
    setDescription(template.desc);
    setTechnologies(techStacks[template.type].slice(0, 3));
  };

  const handleGenerate = async () => {
    if (!projectName || !description) {
      toast({
        title: 'Ошибка',
        description: 'Заполните название и описание проекта',
        variant: 'destructive'
      });
      return;
    }

    const apiKey = localStorage.getItem('openrouter_api_key');
    if (!apiKey) {
      toast({
        title: 'API ключ не найден',
        description: 'Добавьте OPENROUTER_API_KEY в настройках проекта',
        variant: 'destructive'
      });
      return;
    }

    setIsGenerating(true);
    setGeneratedCode('');

    try {
      const client = createOpenRouterClient(apiKey);
      if (!client) throw new Error('Failed to create OpenRouter client');

      const config = client.getModelConfig(aiModel);
      const systemPrompt = client.getSystemPrompt('create');

      const userPrompt = `
Create a ${projectType} project with the following specifications:

Project Name: ${projectName}
Description: ${description}
Technologies: ${technologies.join(', ') || 'Choose appropriate ones'}
Language: ${language}

Generate:
1. Project structure (folders and files)
2. Main entry point code
3. Configuration files
4. README with setup instructions

Provide clean, production-ready code following best practices.
`;

      let fullResponse = '';

      await client.chatStream(
        {
          model: aiModel,
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt }
          ],
          ...config
        },
        (chunk) => {
          fullResponse += chunk;
          setGeneratedCode(fullResponse);
        }
      );

      const project = await api.createProject({
        name: projectName,
        description: description,
        project_type: projectType,
        technologies: technologies
      });

      await api.createVersion({
        project_id: project.id!,
        change_type: 'creation',
        change_description: 'Initial project creation',
        files_changed: ['project structure'],
        ai_model: aiModel
      });

      toast({
        title: 'Проект создан!',
        description: `${projectName} успешно создан с использованием ${aiModel}`
      });

    } catch (error) {
      console.error('Generation error:', error);
      toast({
        title: 'Ошибка генерации',
        description: error instanceof Error ? error.message : 'Произошла ошибка',
        variant: 'destructive'
      });
    } finally {
      setIsGenerating(false);
    }
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
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Название проекта</Label>
              <Input
                placeholder="Мой крутой проект"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="mt-2"
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
                {techStacks[projectType].map((tech) => (
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

        {generatedCode && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Icon name="Code" size={18} />
                Сгенерированный код
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-xs font-mono max-h-96">
                {generatedCode}
              </pre>
            </CardContent>
          </Card>
        )}
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="Zap" size={18} />
              Шаблоны
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {templates.map((template, idx) => (
              <Card
                key={idx}
                className="cursor-pointer hover:bg-accent transition-colors"
                onClick={() => loadTemplate(template)}
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
              <Icon name="Info" size={18} />
              Как использовать
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-start gap-2">
              <Icon name="Check" className="text-primary mt-0.5" size={16} />
              <span>Опишите проект подробно</span>
            </div>
            <div className="flex items-start gap-2">
              <Icon name="Check" className="text-primary mt-0.5" size={16} />
              <span>Выберите подходящие технологии</span>
            </div>
            <div className="flex items-start gap-2">
              <Icon name="Check" className="text-primary mt-0.5" size={16} />
              <span>AI сгенерирует структуру и код</span>
            </div>
            <div className="flex items-start gap-2">
              <Icon name="Check" className="text-primary mt-0.5" size={16} />
              <span>Проект сохранится в базе</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default CreateProjectForm;
