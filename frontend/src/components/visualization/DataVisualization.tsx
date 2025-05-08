import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Grid,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Divider,
  Slider,
  Tabs,
  Tab,
  IconButton,
  Tooltip as MuiTooltip
} from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale,
  ScatterController,
  BubbleController,
  BarController,
  LineController,
  PieController,
  DoughnutController,
  PolarAreaController,
  RadarController,
  ScatterDataPoint,
  BubbleDataPoint
} from 'chart.js';
import { Bar, Line, Pie, Doughnut, Scatter, Bubble, Radar, PolarArea } from 'react-chartjs-2';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SaveIcon from '@mui/icons-material/Save';
import ShareIcon from '@mui/icons-material/Share';
import SettingsIcon from '@mui/icons-material/Settings';
import ColorLensIcon from '@mui/icons-material/ColorLens';
import TuneIcon from '@mui/icons-material/Tune';

// 检查是否在浏览器环境中
const isBrowser = typeof window !== 'undefined';

// 只在浏览器环境中注册Chart.js插件
if (isBrowser) {
  // 动态导入插件
  import('chartjs-plugin-datalabels').then((ChartDataLabels) => {
    ChartJS.register(ChartDataLabels.default);
  });

  import('chartjs-plugin-zoom').then((zoomPlugin) => {
    ChartJS.register(zoomPlugin.default);
  });
}

// 注册Chart.js基本组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  RadialLinearScale,
  ScatterController,
  BubbleController,
  BarController,
  LineController,
  PieController,
  DoughnutController,
  PolarAreaController,
  RadarController,
  Title,
  Tooltip,
  Legend
);

// 图表类型
type ChartType = 'bar' | 'line' | 'pie' | 'doughnut' | 'scatter' | 'bubble' | 'radar' | 'polarArea' | 'table';

// 图表配置接口
interface ChartConfig {
  title: string;
  showLegend: boolean;
  showDataLabels: boolean;
  enableZoom: boolean;
  backgroundColor: string[];
  borderColor: string[];
  xAxisLabel: string;
  yAxisLabel: string;
  aspectRatio: number;
  animation: boolean;
}

// 默认图表配置
const defaultChartConfig: ChartConfig = {
  title: '',
  showLegend: true,
  showDataLabels: false,
  enableZoom: false,
  backgroundColor: [],
  borderColor: [],
  xAxisLabel: '',
  yAxisLabel: '',
  aspectRatio: 2,
  animation: true
};

// 数据可视化组件属性
interface DataVisualizationProps {
  data: any;
  title?: string;
  initialChartType?: ChartType;
  allowConfiguring?: boolean;
  onSave?: (chartData: any, chartType: ChartType, config: ChartConfig) => void;
}

// 判断数据是否适合特定图表类型
const isDataSuitableForChart = (data: any, chartType: ChartType): boolean => {
  if (!data) return false;

  // 对于表格数据，任何结构化数据都可以
  if (chartType === 'table') return true;

  // 检查数据是否为数组
  if (Array.isArray(data)) {
    // 对于饼图、环形图和极坐标图，数据需要是简单的键值对
    if (chartType === 'pie' || chartType === 'doughnut' || chartType === 'polarArea') {
      return data.length > 0 && data.length <= 15; // 限制数据点数量
    }

    // 对于散点图和气泡图，数据需要有x和y坐标
    if (chartType === 'scatter' || chartType === 'bubble') {
      if (data.length === 0) return false;

      // 检查数据是否有x和y属性
      if (typeof data[0] === 'object' && data[0] !== null) {
        const hasXY = data.every((item: any) =>
          typeof item.x !== 'undefined' &&
          typeof item.y !== 'undefined'
        );

        // 气泡图还需要r属性
        if (chartType === 'bubble') {
          return hasXY && data.every((item: any) => typeof item.r !== 'undefined');
        }

        return hasXY;
      }

      // 如果数据是二维数组，也可以用于散点图
      if (Array.isArray(data[0]) && data[0].length >= 2) {
        return true;
      }

      return false;
    }

    // 对于雷达图，数据需要有多个维度
    if (chartType === 'radar') {
      if (data.length === 0) return false;

      // 如果数据是对象数组，检查是否有多个数值属性
      if (typeof data[0] === 'object' && data[0] !== null) {
        const keys = Object.keys(data[0]);
        const numericKeys = keys.filter(key =>
          typeof data[0][key] === 'number'
        );

        return numericKeys.length >= 3; // 雷达图至少需要3个维度
      }

      return false;
    }

    // 对于柱状图和折线图，数据需要有多个数据点
    return data.length > 0;
  }

  // 检查数据是否为对象
  if (typeof data === 'object' && data !== null) {
    // 对于饼图、环形图和极坐标图，对象的键值对可以直接使用
    if (chartType === 'pie' || chartType === 'doughnut' || chartType === 'polarArea') {
      const keys = Object.keys(data);
      return keys.length > 0 && keys.length <= 15; // 限制数据点数量
    }

    // 对于雷达图，需要检查对象是否有多个数值属性
    if (chartType === 'radar') {
      const keys = Object.keys(data);
      const numericValues = keys.filter(key =>
        typeof data[key] === 'number'
      );

      return numericValues.length >= 3; // 雷达图至少需要3个维度
    }

    // 对于柱状图和折线图，需要检查对象是否有可用的数据结构
    return Object.keys(data).length > 0;
  }

  return false;
};

// 准备图表数据
const prepareChartData = (data: any, chartType: ChartType, config?: Partial<ChartConfig>) => {
  // 如果数据为空，返回空数据
  if (!data) return { labels: [], datasets: [] };

  // 生成随机颜色
  const generateColors = (count: number) => {
    // 如果配置中提供了颜色，使用配置的颜色
    if (config?.backgroundColor && config.backgroundColor.length >= count) {
      return config.backgroundColor.slice(0, count);
    }

    // 否则生成随机颜色
    const colors = [];
    for (let i = 0; i < count; i++) {
      const r = Math.floor(Math.random() * 200);
      const g = Math.floor(Math.random() * 200);
      const b = Math.floor(Math.random() * 200);
      colors.push(`rgba(${r}, ${g}, ${b}, 0.6)`);
    }
    return colors;
  };

  // 生成边框颜色
  const generateBorderColors = (backgroundColors: string[]) => {
    // 如果配置中提供了边框颜色，使用配置的颜色
    if (config?.borderColor && config.borderColor.length >= backgroundColors.length) {
      return config.borderColor.slice(0, backgroundColors.length);
    }

    // 否则基于背景色生成边框色
    return backgroundColors.map(color => color.replace('0.6', '1'));
  };

  // 处理数组数据
  if (Array.isArray(data)) {
    // 处理散点图和气泡图数据
    if ((chartType === 'scatter' || chartType === 'bubble') && data.length > 0) {
      // 检查数据格式
      if (typeof data[0] === 'object' && data[0] !== null) {
        // 如果数据已经有x和y属性
        if (typeof data[0].x !== 'undefined' && typeof data[0].y !== 'undefined') {
          const colors = generateColors(1);
          const borderColors = generateBorderColors(colors);

          // 对于气泡图，确保有r属性
          if (chartType === 'bubble' && typeof data[0].r === 'undefined') {
            // 如果没有r属性，添加默认值
            data = data.map((item: any) => ({
              ...item,
              r: 5 // 默认半径
            }));
          }

          return {
            datasets: [
              {
                label: '数据点',
                data: data,
                backgroundColor: colors[0],
                borderColor: borderColors[0],
                borderWidth: 1,
                pointRadius: 5,
                pointHoverRadius: 8
              }
            ]
          };
        }

        // 如果数据是对象数组但没有x和y属性，尝试转换
        const numericKeys = Object.keys(data[0]).filter(key =>
          typeof data[0][key] === 'number'
        );

        if (numericKeys.length >= 2) {
          const xKey = numericKeys[0];
          const yKey = numericKeys[1];

          // 对于气泡图，使用第三个数值属性作为半径
          const rKey = chartType === 'bubble' && numericKeys.length > 2 ? numericKeys[2] : null;

          const transformedData = data.map((item: any) => ({
            x: item[xKey],
            y: item[yKey],
            ...(rKey ? { r: item[rKey] } : { r: 5 })
          }));

          const colors = generateColors(1);
          const borderColors = generateBorderColors(colors);

          return {
            datasets: [
              {
                label: `${xKey} vs ${yKey}`,
                data: transformedData,
                backgroundColor: colors[0],
                borderColor: borderColors[0],
                borderWidth: 1,
                pointRadius: 5,
                pointHoverRadius: 8
              }
            ]
          };
        }
      }

      // 如果数据是二维数组
      if (Array.isArray(data[0]) && data[0].length >= 2) {
        const transformedData = data.map((item: any) => ({
          x: item[0],
          y: item[1],
          ...(item.length > 2 && chartType === 'bubble' ? { r: item[2] } : { r: 5 })
        }));

        const colors = generateColors(1);
        const borderColors = generateBorderColors(colors);

        return {
          datasets: [
            {
              label: '数据点',
              data: transformedData,
              backgroundColor: colors[0],
              borderColor: borderColors[0],
              borderWidth: 1,
              pointRadius: 5,
              pointHoverRadius: 8
            }
          ]
        };
      }
    }

    // 处理雷达图数据
    if (chartType === 'radar' && data.length > 0) {
      if (typeof data[0] === 'object' && data[0] !== null) {
        const keys = Object.keys(data[0]);
        const numericKeys = keys.filter(key =>
          typeof data[0][key] === 'number'
        );

        if (numericKeys.length >= 3) {
          // 使用第一个非数值键作为标签
          const labelKey = keys.find(key => !numericKeys.includes(key)) || keys[0];

          // 提取标签
          const labels = numericKeys;

          // 为每个对象创建一个数据集
          const datasets = data.map((item: any, index: number) => {
            const color = `rgba(${index * 50 % 200}, ${(index * 80 + 40) % 200}, ${(index * 120 + 80) % 200}, 0.6)`;
            return {
              label: item[labelKey] || `数据集 ${index + 1}`,
              data: numericKeys.map(key => item[key]),
              backgroundColor: color.replace('0.6', '0.2'),
              borderColor: color.replace('0.6', '1'),
              borderWidth: 1,
              pointBackgroundColor: color,
              pointBorderColor: '#fff',
              pointHoverBackgroundColor: '#fff',
              pointHoverBorderColor: color
            };
          });

          return { labels, datasets };
        }
      }
    }

    // 如果数组元素是对象
    if (data.length > 0 && typeof data[0] === 'object' && data[0] !== null) {
      // 获取所有对象的键
      const keys = Object.keys(data[0]);

      // 选择第一个键作为标签，其余键作为数据
      const labelKey = keys[0];
      const dataKeys = keys.slice(1).filter(key => typeof data[0][key] === 'number');

      if (dataKeys.length === 0) {
        // 如果没有数值类型的键，尝试使用对象计数
        const labels = data.map((item: any) => item[labelKey]);
        const values = data.map(() => 1); // 每个项目计数为1

        const colors = generateColors(labels.length);
        const borderColors = generateBorderColors(colors);

        return {
          labels,
          datasets: [
            {
              label: '计数',
              data: values,
              backgroundColor: colors,
              borderColor: borderColors,
              borderWidth: 1
            }
          ]
        };
      }

      // 提取标签和数据
      const labels = data.map((item: any) => item[labelKey]);

      // 为每个数据键创建一个数据集
      const datasets = dataKeys.map((key, index) => {
        const colors = generateColors(1);
        const borderColors = generateBorderColors(colors);

        return {
          label: key,
          data: data.map((item: any) => item[key]),
          backgroundColor: colors[0],
          borderColor: borderColors[0],
          borderWidth: 1
        };
      });

      return { labels, datasets };
    }

    // 如果数组元素是基本类型
    const labels = data.map((_: any, index: number) => `项目 ${index + 1}`);
    const values = data.filter((value: any) => typeof value === 'number');

    if (values.length === 0) {
      // 如果没有数值，使用计数
      const counts: { [key: string]: number } = {};
      data.forEach((item: any) => {
        const key = String(item);
        counts[key] = (counts[key] || 0) + 1;
      });

      const uniqueLabels = Object.keys(counts);
      const uniqueValues = uniqueLabels.map(label => counts[label]);
      const colors = generateColors(uniqueLabels.length);

      return {
        labels: uniqueLabels,
        datasets: [
          {
            label: '计数',
            data: uniqueValues,
            backgroundColor: colors,
            borderColor: colors.map(color => color.replace('0.6', '1')),
            borderWidth: 1
          }
        ]
      };
    }

    const colors = generateColors(values.length);

    return {
      labels,
      datasets: [
        {
          label: '数值',
          data: values,
          backgroundColor: colors,
          borderColor: colors.map(color => color.replace('0.6', '1')),
          borderWidth: 1
        }
      ]
    };
  }

  // 处理对象数据
  if (typeof data === 'object' && data !== null) {
    const keys = Object.keys(data);
    const values = keys.map(key => data[key]).filter(value => typeof value === 'number');

    // 处理雷达图数据
    if (chartType === 'radar' && values.length >= 3) {
      const colors = generateColors(1);
      const borderColors = generateBorderColors(colors);

      return {
        labels: keys,
        datasets: [
          {
            label: '数据',
            data: values,
            backgroundColor: colors[0].replace('0.6', '0.2'),
            borderColor: borderColors[0],
            borderWidth: 1,
            pointBackgroundColor: colors[0],
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: colors[0]
          }
        ]
      };
    }

    // 处理极坐标图数据
    if (chartType === 'polarArea') {
      const colors = generateColors(values.length);
      const borderColors = generateBorderColors(colors);

      return {
        labels: keys,
        datasets: [
          {
            data: values,
            backgroundColor: colors,
            borderColor: borderColors,
            borderWidth: 1
          }
        ]
      };
    }

    if (values.length === 0) {
      // 如果没有数值，尝试使用嵌套对象
      const nestedData: { [key: string]: number } = {};

      keys.forEach(key => {
        if (typeof data[key] === 'object' && data[key] !== null) {
          const nestedKeys = Object.keys(data[key]);
          nestedKeys.forEach(nestedKey => {
            if (typeof data[key][nestedKey] === 'number') {
              nestedData[`${key}.${nestedKey}`] = data[key][nestedKey];
            }
          });
        }
      });

      const nestedKeys = Object.keys(nestedData);
      const nestedValues = nestedKeys.map(key => nestedData[key]);

      if (nestedValues.length > 0) {
        const colors = generateColors(nestedValues.length);
        const borderColors = generateBorderColors(colors);

        return {
          labels: nestedKeys,
          datasets: [
            {
              label: '数值',
              data: nestedValues,
              backgroundColor: colors,
              borderColor: borderColors,
              borderWidth: 1
            }
          ]
        };
      }

      // 如果仍然没有数值，使用键计数
      const colors = generateColors(keys.length);
      const borderColors = generateBorderColors(colors);

      return {
        labels: keys,
        datasets: [
          {
            label: '计数',
            data: keys.map(() => 1),
            backgroundColor: colors,
            borderColor: borderColors,
            borderWidth: 1
          }
        ]
      };
    }

    const colors = generateColors(values.length);
    const borderColors = generateBorderColors(colors);

    return {
      labels: keys,
      datasets: [
        {
          label: '数值',
          data: values,
          backgroundColor: colors,
          borderColor: borderColors,
          borderWidth: 1
        }
      ]
    };
  }

  // 默认返回空数据
  return { labels: [], datasets: [] };
};

// 图表配置面板组件
interface ChartConfigPanelProps {
  config: ChartConfig;
  onChange: (config: ChartConfig) => void;
  chartType: ChartType;
}

const ChartConfigPanel: React.FC<ChartConfigPanelProps> = ({ config, onChange, chartType }) => {
  // 处理配置变更
  const handleConfigChange = (key: keyof ChartConfig, value: any) => {
    onChange({
      ...config,
      [key]: value
    });
  };

  // 处理颜色变更
  const handleColorChange = (index: number, color: string, isBackground: boolean) => {
    const colors = isBackground ? [...config.backgroundColor] : [...config.borderColor];
    colors[index] = color;

    handleConfigChange(isBackground ? 'backgroundColor' : 'borderColor', colors);
  };

  return (
    <Box>
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TuneIcon sx={{ mr: 1 }} />
            <Typography>基本设置</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                label="图表标题"
                value={config.title}
                onChange={(e) => handleConfigChange('title', e.target.value)}
                fullWidth
                size="small"
              />
            </Grid>
            <Grid item xs={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={config.showLegend}
                    onChange={(e) => handleConfigChange('showLegend', e.target.checked)}
                  />
                }
                label="显示图例"
              />
            </Grid>
            <Grid item xs={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={config.showDataLabels}
                    onChange={(e) => handleConfigChange('showDataLabels', e.target.checked)}
                  />
                }
                label="显示数据标签"
              />
            </Grid>
            <Grid item xs={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={config.enableZoom}
                    onChange={(e) => handleConfigChange('enableZoom', e.target.checked)}
                  />
                }
                label="启用缩放"
              />
            </Grid>
            <Grid item xs={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={config.animation}
                    onChange={(e) => handleConfigChange('animation', e.target.checked)}
                  />
                }
                label="启用动画"
              />
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {(chartType === 'bar' || chartType === 'line') && (
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <TuneIcon sx={{ mr: 1 }} />
              <Typography>坐标轴设置</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="X轴标签"
                  value={config.xAxisLabel}
                  onChange={(e) => handleConfigChange('xAxisLabel', e.target.value)}
                  fullWidth
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Y轴标签"
                  value={config.yAxisLabel}
                  onChange={(e) => handleConfigChange('yAxisLabel', e.target.value)}
                  fullWidth
                  size="small"
                />
              </Grid>
              <Grid item xs={12}>
                <Typography gutterBottom>宽高比</Typography>
                <Slider
                  value={config.aspectRatio}
                  min={0.5}
                  max={3}
                  step={0.1}
                  onChange={(_, value) => handleConfigChange('aspectRatio', value)}
                  valueLabelDisplay="auto"
                />
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
      )}

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <ColorLensIcon sx={{ mr: 1 }} />
            <Typography>颜色设置</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="subtitle2" gutterBottom>
            背景颜色
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
            {config.backgroundColor.map((color, index) => (
              <Box
                key={index}
                sx={{
                  width: 30,
                  height: 30,
                  bgcolor: color,
                  border: '1px solid #ddd',
                  borderRadius: 1,
                  cursor: 'pointer'
                }}
                onClick={() => {
                  // 打开颜色选择器
                  const input = document.createElement('input');
                  input.type = 'color';
                  input.value = color.replace(/rgba\((\d+), (\d+), (\d+), [\d\.]+\)/, 'rgb($1, $2, $3)');
                  input.addEventListener('input', (e) => {
                    const target = e.target as HTMLInputElement;
                    const rgb = target.value;
                    // 转换为rgba
                    const rgba = rgb.replace(/rgb\((\d+), (\d+), (\d+)\)/, 'rgba($1, $2, $3, 0.6)');
                    handleColorChange(index, rgba, true);
                  });
                  input.click();
                }}
              />
            ))}
            {config.backgroundColor.length === 0 && (
              <Typography variant="body2" color="text.secondary">
                没有可用的颜色
              </Typography>
            )}
          </Box>

          <Typography variant="subtitle2" gutterBottom>
            边框颜色
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {config.borderColor.map((color, index) => (
              <Box
                key={index}
                sx={{
                  width: 30,
                  height: 30,
                  bgcolor: color,
                  border: '1px solid #ddd',
                  borderRadius: 1,
                  cursor: 'pointer'
                }}
                onClick={() => {
                  // 打开颜色选择器
                  const input = document.createElement('input');
                  input.type = 'color';
                  input.value = color.replace(/rgba\((\d+), (\d+), (\d+), [\d\.]+\)/, 'rgb($1, $2, $3)');
                  input.addEventListener('input', (e) => {
                    const target = e.target as HTMLInputElement;
                    const rgb = target.value;
                    // 转换为rgba
                    const rgba = rgb.replace(/rgb\((\d+), (\d+), (\d+)\)/, 'rgba($1, $2, $3, 1)');
                    handleColorChange(index, rgba, false);
                  });
                  input.click();
                }}
              />
            ))}
            {config.borderColor.length === 0 && (
              <Typography variant="body2" color="text.secondary">
                没有可用的颜色
              </Typography>
            )}
          </Box>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

// 数据可视化组件
const DataVisualization: React.FC<DataVisualizationProps> = ({
  data,
  title,
  initialChartType = 'bar',
  allowConfiguring = true,
  onSave
}) => {
  const [chartType, setChartType] = useState<ChartType>(initialChartType);
  const [chartData, setChartData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [showConfig, setShowConfig] = useState(false);
  const [chartConfig, setChartConfig] = useState<ChartConfig>({...defaultChartConfig, title: title || ''});

  // 获取可用的图表类型
  const availableChartTypes = [
    { value: 'bar', label: '柱状图' },
    { value: 'line', label: '折线图' },
    { value: 'pie', label: '饼图' },
    { value: 'doughnut', label: '环形图' },
    { value: 'scatter', label: '散点图' },
    { value: 'bubble', label: '气泡图' },
    { value: 'radar', label: '雷达图' },
    { value: 'polarArea', label: '极坐标图' },
    { value: 'table', label: '表格' }
  ].filter(type => isDataSuitableForChart(data, type.value as ChartType));

  // 处理图表类型变更
  const handleChartTypeChange = (event: SelectChangeEvent) => {
    setChartType(event.target.value as ChartType);
  };

  // 准备图表数据
  useEffect(() => {
    try {
      if (chartType !== 'table') {
        const preparedData = prepareChartData(data, chartType, chartConfig);
        setChartData(preparedData);

        // 更新图表配置中的颜色
        if (preparedData.datasets && preparedData.datasets.length > 0) {
          const backgroundColors: string[] = [];
          const borderColors: string[] = [];

          preparedData.datasets.forEach((dataset: any) => {
            if (Array.isArray(dataset.backgroundColor)) {
              backgroundColors.push(...dataset.backgroundColor);
            } else if (dataset.backgroundColor) {
              backgroundColors.push(dataset.backgroundColor);
            }

            if (Array.isArray(dataset.borderColor)) {
              borderColors.push(...dataset.borderColor);
            } else if (dataset.borderColor) {
              borderColors.push(dataset.borderColor);
            }
          });

          setChartConfig(prev => ({
            ...prev,
            backgroundColor: backgroundColors,
            borderColor: borderColors
          }));
        }

        setError(null);
      }
    } catch (err: any) {
      console.error('准备图表数据时出错:', err);
      setError('无法为当前数据创建图表');
    }
  }, [data, chartType, chartConfig.title, chartConfig.showLegend, chartConfig.showDataLabels, chartConfig.enableZoom, chartConfig.xAxisLabel, chartConfig.yAxisLabel, chartConfig.aspectRatio, chartConfig.animation]);

  // 如果没有可用的图表类型，显示提示
  if (availableChartTypes.length === 0) {
    return (
      <Alert severity="info">
        当前数据不适合可视化展示
      </Alert>
    );
  }

  // 准备图表选项
  const getChartOptions = () => {
    const baseOptions: any = {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: chartConfig.aspectRatio,
      animation: chartConfig.animation ? {
        duration: 1000,
        easing: 'easeOutQuart'
      } : false,
      plugins: {
        legend: {
          display: chartConfig.showLegend
        },
        title: {
          display: !!chartConfig.title,
          text: chartConfig.title
        },
        datalabels: {
          display: chartConfig.showDataLabels,
          color: '#fff',
          font: {
            weight: 'bold'
          },
          formatter: (value: any) => {
            if (typeof value === 'number') {
              return value.toLocaleString();
            }
            return value;
          }
        },
        zoom: {
          pan: {
            enabled: chartConfig.enableZoom,
            mode: 'xy' as const
          },
          zoom: {
            wheel: {
              enabled: chartConfig.enableZoom
            },
            pinch: {
              enabled: chartConfig.enableZoom
            },
            mode: 'xy' as const
          }
        }
      }
    };

    // 为柱状图和折线图添加坐标轴标签
    if (chartType === 'bar' || chartType === 'line') {
      return {
        ...baseOptions,
        scales: {
          x: {
            title: {
              display: !!chartConfig.xAxisLabel,
              text: chartConfig.xAxisLabel
            }
          },
          y: {
            title: {
              display: !!chartConfig.yAxisLabel,
              text: chartConfig.yAxisLabel
            }
          }
        }
      };
    }

    return baseOptions;
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box sx={{ flex: 1 }}>
          <FormControl fullWidth size="small">
            <InputLabel>图表类型</InputLabel>
            <Select
              value={chartType}
              label="图表类型"
              onChange={handleChartTypeChange}
            >
              {availableChartTypes.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        {allowConfiguring && (
          <Box sx={{ ml: 1, display: 'flex' }}>
            <MuiTooltip title="图表设置">
              <IconButton onClick={() => setShowConfig(!showConfig)}>
                <SettingsIcon />
              </IconButton>
            </MuiTooltip>

            {onSave && (
              <MuiTooltip title="保存图表">
                <IconButton onClick={() => onSave(chartData, chartType, chartConfig)}>
                  <SaveIcon />
                </IconButton>
              </MuiTooltip>
            )}
          </Box>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={2}>
        {showConfig && (
          <Grid item xs={12} md={4}>
            <ChartConfigPanel
              config={chartConfig}
              onChange={setChartConfig}
              chartType={chartType}
            />
          </Grid>
        )}

        <Grid item xs={12} md={showConfig ? 8 : 12}>
          <Box sx={{ height: 400, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            {chartType === 'bar' && chartData && (
              <Bar data={chartData} options={getChartOptions()} />
            )}
            {chartType === 'line' && chartData && (
              <Line data={chartData} options={getChartOptions()} />
            )}
            {chartType === 'pie' && chartData && (
              <Pie data={chartData} options={getChartOptions()} />
            )}
            {chartType === 'doughnut' && chartData && (
              <Doughnut data={chartData} options={getChartOptions()} />
            )}
            {chartType === 'scatter' && chartData && (
              <Scatter data={chartData} options={getChartOptions()} />
            )}
            {chartType === 'bubble' && chartData && (
              <Bubble data={chartData} options={getChartOptions()} />
            )}
            {chartType === 'radar' && chartData && (
              <Radar data={chartData} options={getChartOptions()} />
            )}
            {chartType === 'polarArea' && chartData && (
              <PolarArea data={chartData} options={getChartOptions()} />
            )}
            {chartType === 'table' && (
              <Box sx={{ width: '100%', overflowX: 'auto' }}>
                <TableView data={data} />
              </Box>
            )}
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

// 表格视图组件
const TableView: React.FC<{ data: any }> = ({ data }) => {
  // 如果数据为空，显示提示
  if (!data) {
    return <Typography>无数据</Typography>;
  }

  // 处理数组数据
  if (Array.isArray(data)) {
    // 如果数组为空，显示提示
    if (data.length === 0) {
      return <Typography>空数组</Typography>;
    }

    // 如果数组元素是对象
    if (typeof data[0] === 'object' && data[0] !== null) {
      const headers = Object.keys(data[0]);

      return (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              {headers.map((header, index) => (
                <th key={index} style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((item, rowIndex) => (
              <tr key={rowIndex}>
                {headers.map((header, colIndex) => (
                  <td key={colIndex} style={{ border: '1px solid #ddd', padding: '8px' }}>
                    {typeof item[header] === 'object' ? JSON.stringify(item[header]) : String(item[header])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      );
    }

    // 如果数组元素是基本类型
    return (
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>索引</th>
            <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>值</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index}>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>{index}</td>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                {typeof item === 'object' ? JSON.stringify(item) : String(item)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  }

  // 处理对象数据
  if (typeof data === 'object' && data !== null) {
    const keys = Object.keys(data);

    return (
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>键</th>
            <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>值</th>
          </tr>
        </thead>
        <tbody>
          {keys.map((key, index) => (
            <tr key={index}>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>{key}</td>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                {typeof data[key] === 'object' ? JSON.stringify(data[key]) : String(data[key])}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  }

  // 处理其他类型数据
  return <Typography>不支持的数据类型: {typeof data}</Typography>;
};

export default DataVisualization;
