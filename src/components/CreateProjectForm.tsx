import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';
import BuildProgress from '@/components/BuildProgress';
import AgentConsole from '@/components/AgentConsole';
import ProjectResult from '@/components/ProjectResult';
import { useToast } from '@/hooks/use-toast';

const ORCHESTRATOR_URL = 'https://functions.poehali.dev/cc5ecac6-d2e9-4ad0-aefb-cd92daf9e392';

interface CreateProjectFormProps {
  aiModel: string;
  language: string;
}

type BuildStatus = 'idle' | 'building' | 'completed' | 'failed';

interface BuildState {
  sessionId: string | null;
  status: BuildStatus;
  progress: number;
  currentStep: string;
  steps: Array<{ key: string; label: string; status: string; duration_ms?: number }>;
  agentLogs: Array<{ agent: string; action: string; message: string; status: string; timestamp: string | null }>;
  result: {
    appUrl: string;
    githubUrl: string;
    filesCount: number;
    buildTime: number;
    costUsd: number;
  } | null;
  error: string | null;
}

const CreateProjectForm = ({ aiModel, language }: CreateProjectFormProps) => {
  const [projectName, setProjectName] = useState('');
  const [description, setDescription] = useState('');
  const { toast } = useToast();

  const [build, setBuild] = useState<BuildState>({
    sessionId: null,
    status: 'idle',
    progress: 0,
    currentStep: '',
    steps: [],
    agentLogs: [],
    result: null,
    error: null,
  });

  const templates = [
    { name: 'Todo-приложение', desc: 'Список задач с авторизацией и тёмной темой' },
    { name: 'Лендинг', desc: 'Одностраничный сайт с формой обратной связи и анимациями' },
    { name: 'CRM-система', desc: 'Управление клиентами, сделками и аналитика' },
    { name: 'Чат', desc: 'Мессенджер с комнатами и онлайн-статусами' },
  ];

  const loadTemplate = (template: typeof templates[0]) => {
    setProjectName(template.name);
    setDescription(template.desc);
  };

  const pollStatus = useCallback(async (sessionId: string) => {
    try {
      const response = await fetch(`${ORCHESTRATOR_URL}?action=status&session_id=${sessionId}`);
      if (!response.ok) return;

      const data = await response.json();

      setBuild(prev => ({
        ...prev,
        progress: data.progress || 0,
        currentStep: data.current_step || '',
        steps: data.steps || prev.steps,
        agentLogs: data.agent_logs || prev.agentLogs,
      }));

      if (data.status === 'completed') {
        setBuild(prev => ({
          ...prev,
          status: 'completed',
          result: {
            appUrl: data.app_url || '',
            githubUrl: data.github_url || '',
            filesCount: data.files_count || 0,
            buildTime: data.completed_at && data.started_at
              ? Math.round((new Date(data.completed_at).getTime() - new Date(data.started_at).getTime()) / 1000)
              : 0,
            costUsd: data.cost_usd || 0,
          },
        }));
        return;
      }

      if (data.status === 'failed') {
        setBuild(prev => ({
          ...prev,
          status: 'failed',
          error: data.error_message || 'Неизвестная ошибка',
        }));
        return;
      }

      setTimeout(() => pollStatus(sessionId), 2000);
    } catch {
      setTimeout(() => pollStatus(sessionId), 3000);
    }
  }, []);

  const handleBuild = async () => {
    if (!projectName || !description) {
      toast({ title: 'Заполните название и описание', variant: 'destructive' });
      return;
    }

    setBuild({
      sessionId: null,
      status: 'building',
      progress: 0,
      currentStep: 'Запуск...',
      steps: [],
      agentLogs: [],
      result: null,
      error: null,
    });

    try {
      const response = await fetch(ORCHESTRATOR_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'create_project',
          user_query: description,
          project_name: projectName,
          ai_model: aiModel,
          language: language,
        }),
      });

      const data = await response.json();

      if (data.session_id && data.status === 'completed') {
        setBuild(prev => ({
          ...prev,
          sessionId: data.session_id,
          status: 'completed',
          progress: 1,
          currentStep: 'Готово!',
          result: {
            appUrl: data.app_url || '',
            githubUrl: data.github_url || '',
            filesCount: data.files_count || 0,
            buildTime: data.build_time_seconds || 0,
            costUsd: 0,
          },
        }));
        pollStatus(data.session_id);
        return;
      }

      if (data.error) {
        setBuild(prev => ({
          ...prev,
          status: 'failed',
          error: data.error,
        }));
        return;
      }

      if (data.session_id) {
        setBuild(prev => ({ ...prev, sessionId: data.session_id }));
        pollStatus(data.session_id);
      }
    } catch (error) {
      setBuild(prev => ({
        ...prev,
        status: 'failed',
        error: error instanceof Error ? error.message : 'Ошибка соединения',
      }));
    }
  };

  const handleReset = () => {
    setBuild({
      sessionId: null,
      status: 'idle',
      progress: 0,
      currentStep: '',
      steps: [],
      agentLogs: [],
      result: null,
      error: null,
    });
  };

  if (build.status === 'completed' && build.result) {
    return (
      <div className="space-y-6">
        <ProjectResult
          appUrl={build.result.appUrl}
          githubUrl={build.result.githubUrl}
          filesCount={build.result.filesCount}
          buildTime={build.result.buildTime}
          costUsd={build.result.costUsd}
          projectName={projectName}
        />
        <AgentConsole logs={build.agentLogs} isActive={false} />
        <Button variant="outline" onClick={handleReset} className="w-full">
          <Icon name="Plus" size={16} className="mr-2" />
          Создать ещё один проект
        </Button>
      </div>
    );
  }

  if (build.status === 'building') {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Icon name="Loader2" size={20} className="animate-spin" />
              Сборка: {projectName}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              AI-команда из 6 агентов автономно создаёт ваше приложение...
            </p>
          </CardContent>
        </Card>

        {build.steps.length > 0 && (
          <BuildProgress
            steps={build.steps}
            progress={build.progress}
            currentStep={build.currentStep}
          />
        )}

        <AgentConsole logs={build.agentLogs} isActive={true} />
      </div>
    );
  }

  if (build.status === 'failed') {
    return (
      <div className="space-y-6">
        <Card className="border-red-200 dark:border-red-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <Icon name="XCircle" size={20} />
              Ошибка сборки
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">{build.error}</p>
            <Button variant="outline" onClick={handleReset}>
              <Icon name="RotateCcw" size={16} className="mr-2" />
              Попробовать снова
            </Button>
          </CardContent>
        </Card>
        {build.agentLogs.length > 0 && (
          <AgentConsole logs={build.agentLogs} isActive={false} />
        )}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Icon name="Rocket" size={20} />
              Создать приложение
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Название проекта</Label>
              <Input
                placeholder="Мой проект"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="mt-2"
              />
            </div>

            <div>
              <Label>Что нужно создать?</Label>
              <Textarea
                placeholder="Опишите своими словами, что должно делать приложение. Например: 'Сделай Todo-лист с авторизацией, тёмной темой и возможностью добавлять задачи в разные категории'"
                className="min-h-32 mt-2"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <Button
              className="w-full"
              size="lg"
              onClick={handleBuild}
              disabled={!projectName || !description}
            >
              <Icon name="Sparkles" size={18} className="mr-2" />
              Собрать приложение
            </Button>

            <p className="text-xs text-muted-foreground text-center">
              AI-команда проанализирует запрос, спроектирует архитектуру, напишет код и задеплоит приложение
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Icon name="Lightbulb" size={16} />
              Шаблоны
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {templates.map((tpl) => (
              <Card
                key={tpl.name}
                className="cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => loadTemplate(tpl)}
              >
                <CardContent className="p-3">
                  <div className="font-medium text-sm">{tpl.name}</div>
                  <div className="text-xs text-muted-foreground">{tpl.desc}</div>
                </CardContent>
              </Card>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Icon name="Bot" size={16} />
              AI-команда
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-xs text-muted-foreground">
            <div className="flex items-center gap-2">
              <Icon name="Brain" size={14} className="text-purple-500" />
              <span>Архитектор — проектирует структуру</span>
            </div>
            <div className="flex items-center gap-2">
              <Icon name="Database" size={14} className="text-orange-500" />
              <span>БД-специалист — создаёт схему</span>
            </div>
            <div className="flex items-center gap-2">
              <Icon name="Server" size={14} className="text-green-500" />
              <span>Backend — пишет серверный код</span>
            </div>
            <div className="flex items-center gap-2">
              <Icon name="Layout" size={14} className="text-blue-500" />
              <span>Frontend — создаёт интерфейс</span>
            </div>
            <div className="flex items-center gap-2">
              <Icon name="ShieldCheck" size={14} className="text-yellow-500" />
              <span>Тестировщик — проверяет код</span>
            </div>
            <div className="flex items-center gap-2">
              <Icon name="Rocket" size={14} className="text-red-500" />
              <span>DevOps — деплоит в GitHub</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default CreateProjectForm;
