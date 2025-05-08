/**
 * 数据导出工具
 * 提供将数据导出为不同格式的功能
 */
// 动态导入，避免服务器端渲染问题
let XLSX: any;
let jsPDF: any;
let saveAs: any;

// 检查是否在浏览器环境中
const isBrowser = typeof window !== 'undefined';

// 只在浏览器环境中加载这些库
if (isBrowser) {
  import('xlsx').then(module => {
    XLSX = module;
  });

  import('jspdf').then(module => {
    jsPDF = module.jsPDF;
    import('jspdf-autotable');
  });

  import('file-saver').then(module => {
    saveAs = module.saveAs;
  });
}

/**
 * 导出格式类型
 */
export type ExportFormat = 'json' | 'csv' | 'txt' | 'excel' | 'pdf';

/**
 * 导出选项
 */
export interface ExportOptions {
  /**
   * 文件名（不包含扩展名）
   */
  fileName?: string;

  /**
   * 是否在文件名中添加时间戳
   */
  addTimestamp?: boolean;

  /**
   * PDF导出选项
   */
  pdfOptions?: {
    /**
     * 标题
     */
    title?: string;

    /**
     * 页面方向 ('portrait' | 'landscape')
     */
    orientation: 'portrait' | 'landscape';

    /**
     * 页面大小 ('a4' | 'letter' | 'legal')
     */
    pageSize?: string;
  };

  /**
   * Excel导出选项
   */
  excelOptions?: {
    /**
     * 工作表名称
     */
    sheetName?: string;

    /**
     * 是否包含表头
     */
    includeHeader?: boolean;
  };
}

/**
 * 将数据导出为文件
 * @param data 要导出的数据
 * @param format 导出格式
 * @param options 导出选项
 */
export function exportData(data: any, format: ExportFormat = 'json', options: ExportOptions = {}): void {
  // 检查是否在浏览器环境中
  if (!isBrowser) {
    console.warn('exportData 只能在浏览器环境中使用');
    return;
  }

  // 准备文件名
  let fileName = options.fileName || 'export';

  // 添加时间戳
  if (options.addTimestamp) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    fileName += `_${timestamp}`;
  }

  // 确保所有依赖库都已加载
  const waitForDependencies = async () => {
    // 等待所有依赖库加载完成
    if (format === 'excel' && !XLSX) {
      XLSX = await import('xlsx');
    }

    if (format === 'pdf' && !jsPDF) {
      const jspdfModule = await import('jspdf');
      jsPDF = jspdfModule.jsPDF;
      await import('jspdf-autotable');
    }

    if (!saveAs) {
      const fileSaverModule = await import('file-saver');
      saveAs = fileSaverModule.saveAs;
    }

    // 执行导出
    switch (format) {
      case 'json':
        exportAsJson(data, fileName);
        break;

      case 'csv':
        exportAsCsv(data, fileName);
        break;

      case 'txt':
        exportAsTxt(data, fileName);
        break;

      case 'excel':
        exportAsExcel(data, fileName, options.excelOptions);
        break;

      case 'pdf':
        exportAsPdf(data, fileName, options.pdfOptions);
        break;

      default:
        throw new Error(`不支持的导出格式: ${format}`);
    }
  };

  // 执行导出
  waitForDependencies();
}

/**
 * 将数据导出为JSON文件
 * @param data 要导出的数据
 * @param fileName 文件名（不包含扩展名）
 */
function exportAsJson(data: any, fileName: string): void {
  if (!isBrowser || !saveAs) return;

  const content = JSON.stringify(data, null, 2);
  const blob = new Blob([content], { type: 'application/json' });
  saveAs(blob, `${fileName}.json`);
}

/**
 * 将数据导出为CSV文件
 * @param data 要导出的数据
 * @param fileName 文件名（不包含扩展名）
 */
function exportAsCsv(data: any, fileName: string): void {
  if (!isBrowser || !saveAs) return;

  const content = convertToCSV(data);
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
  saveAs(blob, `${fileName}.csv`);
}

/**
 * 将数据导出为TXT文件
 * @param data 要导出的数据
 * @param fileName 文件名（不包含扩展名）
 */
function exportAsTxt(data: any, fileName: string): void {
  if (!isBrowser || !saveAs) return;

  const content = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8;' });
  saveAs(blob, `${fileName}.txt`);
}

/**
 * 将数据导出为Excel文件
 * @param data 要导出的数据
 * @param fileName 文件名（不包含扩展名）
 * @param options Excel导出选项
 */
function exportAsExcel(data: any, fileName: string, options?: ExportOptions['excelOptions']): void {
  if (!isBrowser || !XLSX) return;

  // 准备工作表数据
  const wsData = prepareExcelData(data);

  // 创建工作簿
  const wb = XLSX.utils.book_new();

  // 创建工作表
  const ws = XLSX.utils.aoa_to_sheet(wsData);

  // 添加工作表到工作簿
  XLSX.utils.book_append_sheet(wb, ws, options?.sheetName || 'Sheet1');

  // 导出工作簿
  XLSX.writeFile(wb, `${fileName}.xlsx`);
}

/**
 * 将数据导出为PDF文件
 * @param data 要导出的数据
 * @param fileName 文件名（不包含扩展名）
 * @param options PDF导出选项
 */
function exportAsPdf(data: any, fileName: string, options?: ExportOptions['pdfOptions']): void {
  if (!isBrowser || !jsPDF) return;

  // 准备PDF文档
  const orientation = options?.orientation || 'portrait';
  const pageSize = options?.pageSize || 'a4';
  const doc = new jsPDF({
    orientation: orientation,
    unit: 'mm',
    format: pageSize
  });

  // 添加标题
  if (options?.title) {
    doc.setFontSize(18);
    doc.text(options.title, 14, 22);
    doc.setFontSize(12);
  }

  // 准备表格数据
  const tableData = preparePdfData(data);

  // 添加表格
  (doc as any).autoTable({
    head: tableData.headers.length > 0 ? [tableData.headers] : undefined,
    body: tableData.rows,
    startY: options?.title ? 30 : 14,
    margin: { top: 14 },
    styles: { overflow: 'linebreak' },
    headStyles: { fillColor: [66, 139, 202] }
  });

  // 保存PDF
  doc.save(`${fileName}.pdf`);
}

/**
 * 将数据转换为CSV格式
 * @param data 要转换的数据
 * @returns CSV格式的字符串
 */
function convertToCSV(data: any): string {
  // 如果数据为空，返回空字符串
  if (!data) return '';

  // 处理数组数据
  if (Array.isArray(data)) {
    // 如果数组为空，返回空字符串
    if (data.length === 0) return '';

    // 如果数组元素是对象
    if (typeof data[0] === 'object' && data[0] !== null) {
      // 获取所有对象的键
      const headers = Object.keys(data[0]);

      // 创建CSV行
      const csvRows = [
        headers.join(','), // 标题行
        ...data.map(row =>
          headers.map(header => {
            // 处理特殊字符
            const cell = row[header];
            if (cell === null || cell === undefined) return '';
            const cellStr = typeof cell === 'object' ? JSON.stringify(cell) : String(cell);
            return cellStr.includes(',') ? `"${cellStr.replace(/"/g, '""')}"` : cellStr;
          }).join(',')
        )
      ];

      return csvRows.join('\n');
    }

    // 如果数组元素是基本类型
    return data.join('\n');
  }

  // 处理对象数据
  if (typeof data === 'object' && data !== null) {
    // 创建CSV行
    const rows = Object.entries(data).map(([key, value]) => {
      const valueStr = typeof value === 'object' ? JSON.stringify(value) : String(value);
      return `${key},${valueStr.includes(',') ? `"${valueStr.replace(/"/g, '""')}"` : valueStr}`;
    });

    return ['key,value', ...rows].join('\n');
  }

  // 处理其他类型数据
  return String(data);
}

/**
 * 准备Excel数据
 * @param data 要准备的数据
 * @returns 二维数组，第一行为表头，后续行为数据
 */
function prepareExcelData(data: any): any[][] {
  // 如果数据为空，返回空数组
  if (!data) return [[]];

  // 处理数组数据
  if (Array.isArray(data)) {
    // 如果数组为空，返回空数组
    if (data.length === 0) return [[]];

    // 如果数组元素是对象
    if (typeof data[0] === 'object' && data[0] !== null) {
      // 获取所有对象的键作为表头
      const headers = Object.keys(data[0]);

      // 创建表格数据
      return [
        headers, // 表头行
        ...data.map(row =>
          headers.map(header => {
            const cell = row[header];
            if (cell === null || cell === undefined) return '';
            return typeof cell === 'object' ? JSON.stringify(cell) : cell;
          })
        )
      ];
    }

    // 如果数组元素是基本类型，创建带索引的表格
    return [
      ['索引', '值'], // 表头行
      ...data.map((value, index) => [
        index,
        typeof value === 'object' ? JSON.stringify(value) : value
      ])
    ];
  }

  // 处理对象数据
  if (typeof data === 'object' && data !== null) {
    // 创建键值对表格
    return [
      ['键', '值'], // 表头行
      ...Object.entries(data).map(([key, value]) => [
        key,
        typeof value === 'object' ? JSON.stringify(value) : value
      ])
    ];
  }

  // 处理基本类型数据
  return [['值'], [data]];
}

/**
 * 准备PDF表格数据
 * @param data 要准备的数据
 * @returns 包含表头和行数据的对象
 */
function preparePdfData(data: any): { headers: string[], rows: any[][] } {
  // 如果数据为空，返回空数据
  if (!data) return { headers: [], rows: [] };

  // 处理数组数据
  if (Array.isArray(data)) {
    // 如果数组为空，返回空数据
    if (data.length === 0) return { headers: [], rows: [] };

    // 如果数组元素是对象
    if (typeof data[0] === 'object' && data[0] !== null) {
      // 获取所有对象的键作为表头
      const headers = Object.keys(data[0]);

      // 创建行数据
      const rows = data.map(row =>
        headers.map(header => {
          const cell = row[header];
          if (cell === null || cell === undefined) return '';
          return typeof cell === 'object' ? JSON.stringify(cell) : cell;
        })
      );

      return { headers, rows };
    }

    // 如果数组元素是基本类型，创建带索引的表格
    return {
      headers: ['索引', '值'],
      rows: data.map((value, index) => [
        index,
        typeof value === 'object' ? JSON.stringify(value) : value
      ])
    };
  }

  // 处理对象数据
  if (typeof data === 'object' && data !== null) {
    // 创建键值对表格
    return {
      headers: ['键', '值'],
      rows: Object.entries(data).map(([key, value]) => [
        key,
        typeof value === 'object' ? JSON.stringify(value) : value
      ])
    };
  }

  // 处理基本类型数据
  return {
    headers: ['值'],
    rows: [[data]]
  };
}

/**
 * 将HTML表格导出为CSV
 * @param tableId 表格元素的ID
 * @param fileName 文件名（不包含扩展名）
 */
export function exportTableToCSV(tableId: string, fileName: string = 'table'): void {
  // 获取表格元素
  const table = document.getElementById(tableId);
  if (!table) {
    console.error(`找不到ID为 ${tableId} 的表格元素`);
    return;
  }

  // 获取所有行
  const rows = table.querySelectorAll('tr');
  if (rows.length === 0) {
    console.error('表格没有行');
    return;
  }

  // 创建CSV内容
  const csvContent = Array.from(rows).map(row => {
    // 获取所有单元格
    const cells = row.querySelectorAll('th, td');

    // 将单元格内容转换为CSV格式
    return Array.from(cells).map(cell => {
      const text = cell.textContent || '';
      return text.includes(',') ? `"${text.replace(/"/g, '""')}"` : text;
    }).join(',');
  }).join('\n');

  // 导出CSV
  exportData(csvContent, 'csv', { fileName });
}

/**
 * 将HTML元素导出为文本
 * @param elementId 元素的ID
 * @param fileName 文件名（不包含扩展名）
 */
export function exportElementToText(elementId: string, fileName: string = 'text'): void {
  // 获取元素
  const element = document.getElementById(elementId);
  if (!element) {
    console.error(`找不到ID为 ${elementId} 的元素`);
    return;
  }

  // 获取元素文本内容
  const text = element.innerText || element.textContent || '';

  // 导出文本
  exportData(text, 'txt', { fileName });
}

/**
 * 批量导出项目接口
 */
export interface BatchExportItem {
  /**
   * 数据
   */
  data: any;

  /**
   * 文件名（不包含扩展名）
   */
  fileName: string;

  /**
   * 导出格式
   */
  format: ExportFormat;

  /**
   * 导出选项
   */
  options?: ExportOptions;
}

/**
 * 批量导出数据
 * @param items 要导出的项目数组
 * @param zipFileName 压缩文件名（不包含扩展名）
 */
export async function batchExport(items: BatchExportItem[], zipFileName: string = 'export'): Promise<void> {
  // 检查是否在浏览器环境中
  if (!isBrowser) {
    console.warn('batchExport 只能在浏览器环境中使用');
    return;
  }

  try {
    // 确保所有依赖库都已加载
    if (!saveAs) {
      const fileSaverModule = await import('file-saver');
      saveAs = fileSaverModule.saveAs;
    }

    if (!XLSX) {
      XLSX = await import('xlsx');
    }

    if (!jsPDF) {
      const jspdfModule = await import('jspdf');
      jsPDF = jspdfModule.jsPDF;
      await import('jspdf-autotable');
    }

    // 动态导入JSZip库
    const JSZipModule = await import('jszip');
    const JSZip = JSZipModule.default;

    // 创建ZIP文件
    const zip = new JSZip();

    // 处理每个导出项
    for (const item of items) {
      const { data, fileName, format, options } = item;

      // 根据格式准备内容
      let content: string | Blob;
      let extension: string;

      switch (format) {
        case 'json':
          content = JSON.stringify(data, null, 2);
          extension = 'json';
          break;

        case 'csv':
          content = convertToCSV(data);
          extension = 'csv';
          break;

        case 'txt':
          content = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
          extension = 'txt';
          break;

        case 'excel':
          // Excel文件需要特殊处理，使用XLSX库生成
          const wsData = prepareExcelData(data);
          const wb = XLSX.utils.book_new();
          const ws = XLSX.utils.aoa_to_sheet(wsData);
          XLSX.utils.book_append_sheet(wb, ws, options?.excelOptions?.sheetName || 'Sheet1');

          // 将Excel文件转换为二进制数据
          const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
          content = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
          extension = 'xlsx';
          break;

        case 'pdf':
          // PDF文件需要特殊处理，使用jsPDF库生成
          const orientation = options?.pdfOptions?.orientation || 'portrait';
          const pageSize = options?.pdfOptions?.pageSize || 'a4';
          const doc = new jsPDF({
            orientation: orientation,
            unit: 'mm',
            format: pageSize
          });

          // 添加标题
          if (options?.pdfOptions?.title) {
            doc.setFontSize(18);
            doc.text(options.pdfOptions.title, 14, 22);
            doc.setFontSize(12);
          }

          // 准备表格数据
          const tableData = preparePdfData(data);

          // 添加表格
          (doc as any).autoTable({
            head: tableData.headers.length > 0 ? [tableData.headers] : undefined,
            body: tableData.rows,
            startY: options?.pdfOptions?.title ? 30 : 14,
            margin: { top: 14 },
            styles: { overflow: 'linebreak' },
            headStyles: { fillColor: [66, 139, 202] }
          });

          // 将PDF转换为二进制数据
          const pdfBuffer = doc.output('arraybuffer');
          content = new Blob([pdfBuffer], { type: 'application/pdf' });
          extension = 'pdf';
          break;

        default:
          throw new Error(`不支持的导出格式: ${format}`);
      }

      // 添加文件到ZIP
      if (content instanceof Blob) {
        zip.file(`${fileName}.${extension}`, content);
      } else {
        zip.file(`${fileName}.${extension}`, content);
      }
    }

    // 生成ZIP文件
    const zipBlob = await zip.generateAsync({ type: 'blob' });

    // 下载ZIP文件
    saveAs(zipBlob, `${zipFileName}.zip`);

  } catch (error) {
    console.error('批量导出失败:', error);
    throw error;
  }
}
