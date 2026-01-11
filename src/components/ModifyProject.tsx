import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import Icon from '@/components/ui/icon';

interface ModifyProjectProps {
  aiModel: string;
  language: string;
}

const ModifyProject = ({ aiModel, language }: ModifyProjectProps) => {
  const [modifyType, setModifyType] = useState('feature');
  const [instructions, setInstructions] = useState('');

  const modifyTypes = [
    { value: 'feature', label: 'Добавить функцию', icon: 'Plus', desc: 'Новый функционал' },
    { value: 'fix', label: 'Исправить баг', icon: 'Bug', desc: 'Устранение ошибок' },
    { value: 'refactor', label: 'Рефакторинг', icon: 'RefreshCw', desc: 'Улучшение кода' },
    { value: 'optimize', label: 'Оптимизация', icon: 'Zap', desc: 'Повышение производительности' },
  ];

  const recentChanges = [
    { date: '2 часа назад', desc: 'Добавлена авторизация через OAuth', files: 3, icon: 'Lock' },
    { date: 'Вчера', desc: 'Оптимизация загрузки изображений', files: 5, icon: 'Image' },
    { date: '3 дня назад', desc: 'Рефакторинг API модуля', files: 8, icon: 'Code' },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Icon name="Wrench" size={20} />
              Модификация проекта
            </CardTitle>
            <CardDescription>
              Опишите изменения — агент модифицирует код автоматически
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="grid grid-cols-2 gap-3">
                {modifyTypes.map((type) => (
                  <Card
                    key={type.value}
                    className={`cursor-pointer transition-all hover:scale-105 ${
                      modifyType === type.value ? 'ring-2 ring-primary' : ''
                    }`}
                    onClick={() => setModifyType(type.value)}
                  >
                    <CardContent className="pt-4 pb-3">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                          <Icon name={type.icon} className="text-primary" size={16} />
                        </div>
                        <span className="font-medium text-sm">{type.label}</span>
                      </div>
                      <p className="text-xs text-muted-foreground">{type.desc}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            <div>
              <Textarea
                placeholder="Опишите что нужно изменить в проекте..."
                className="min-h-40"
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
              />
            </div>

            <div className="flex gap-2">
              <Select defaultValue="all">
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Все файлы</SelectItem>
                  <SelectItem value="src">Только /src</SelectItem>
                  <SelectItem value="components">Только компоненты</SelectItem>
                  <SelectItem value="specific">Выбрать файлы</SelectItem>
                </SelectContent>
              </Select>

              <Button variant="outline" className="flex-1">
                <Icon name="File" className="mr-2" size={16} />
                Выбрать файлы
              </Button>
            </div>

            <Button className="w-full" size="lg" disabled={!instructions}>
              <Icon name="Play" className="mr-2" size={18} />
              Применить изменения
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="GitBranch" size={18} />
              Предпросмотр изменений
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <div className="flex items-center gap-2">
                  <Icon name="FilePlus" className="text-green-500" size={16} />
                  <code className="text-sm">src/components/Auth.tsx</code>
                </div>
                <Badge variant="outline" className="text-green-500">+127</Badge>
              </div>
              <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <div className="flex items-center gap-2">
                  <Icon name="FileEdit" className="text-blue-500" size={16} />
                  <code className="text-sm">src/utils/api.ts</code>
                </div>
                <Badge variant="outline">±34</Badge>
              </div>
              <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <div className="flex items-center gap-2">
                  <Icon name="FileMinus" className="text-red-500" size={16} />
                  <code className="text-sm">src/legacy/old-auth.ts</code>
                </div>
                <Badge variant="outline" className="text-red-500">-89</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="History" size={18} />
              История изменений
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {recentChanges.map((change, idx) => (
              <Card key={idx} className="cursor-pointer hover:bg-accent transition-colors">
                <CardContent className="pt-3 pb-3">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <Icon name={change.icon} className="text-primary" size={16} />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium mb-1">{change.desc}</p>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>{change.date}</span>
                        <span>•</span>
                        <span>{change.files} файлов</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="Shield" size={18} />
              Безопасный откат
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p className="text-muted-foreground">
              Все изменения создают точку восстановления. Вы можете откатить изменения в любой момент.
            </p>
            <Button variant="outline" className="w-full" size="sm">
              <Icon name="RotateCcw" className="mr-2" size={16} />
              Откатить последние изменения
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ModifyProject;
