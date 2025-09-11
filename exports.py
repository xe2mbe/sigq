import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import io
import base64
import os

class FMREExporter:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
    def export_to_csv(self, df, filename=None):
        """Exporta DataFrame a CSV"""
        if filename is None:
            filename = f"reportes_fmre_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Preparar datos para CSV
        export_df = df.copy()
        if 'timestamp' in export_df.columns:
            export_df['timestamp'] = pd.to_datetime(export_df['timestamp']).dt.strftime('%d/%m/%Y %H:%M:%S')
        
        csv_buffer = io.StringIO()
        export_df.to_csv(csv_buffer, index=False, encoding='utf-8')
        return csv_buffer.getvalue(), filename
    
    def export_to_excel(self, df, filename=None):
        """Exporta DataFrame a Excel"""
        if filename is None:
            filename = f"reportes_fmre_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        excel_buffer = io.BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            # Hoja principal con reportes
            export_df = df.copy()
            if 'timestamp' in export_df.columns:
                export_df['timestamp'] = pd.to_datetime(export_df['timestamp'])
            
            # Reordenar columnas para mejor presentación
            column_order = ['call_sign', 'operator_name', 'estado', 'ciudad', 'zona', 'sistema', 'signal_report', 'region', 'observations', 'timestamp']
            existing_columns = [col for col in column_order if col in export_df.columns]
            # Fallback para datos antiguos que solo tienen qth
            if 'qth' in export_df.columns and 'ciudad' not in export_df.columns:
                export_df['ciudad'] = export_df['qth']
                export_df['estado'] = 'N/A'
            export_df = export_df[existing_columns]
            
            export_df.to_excel(writer, sheet_name='Reportes', index=False)
            
            # Formatear columnas
            worksheet = writer.sheets['Reportes']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        excel_buffer.seek(0)
        return excel_buffer.getvalue(), filename
    
    def export_to_pdf(self, df, stats=None, filename=None):
        """Exporta DataFrame y estadísticas a PDF"""
        if filename is None:
            filename = f"reporte_fmre_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        story = []
        
        # Logo FMRE
        logo_path = os.path.join('assets', 'LogoFMRE_medium.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path)
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 10))
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=1  # Center
        )
        
        story.append(Paragraph("Reporte de Boletín FMRE A.C.", title_style))
        story.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Estadísticas si están disponibles
        if stats:
            story.append(Paragraph("Resumen Estadístico", self.styles['Heading2']))
            
            # Estadísticas generales
            general_data = [
                ['Total de Participantes', str(stats.get('total_participants', 0))],
                ['Total de Reportes', str(stats.get('total_reports', 0))],
            ]
            
            general_table = Table(general_data)
            general_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(general_table)
            story.append(Spacer(1, 15))
            
            # Estadísticas por zona
            if 'by_zona' in stats and not stats['by_zona'].empty:
                story.append(Paragraph("Participantes por Zona", self.styles['Heading3']))
                zona_data = []
                for _, row in stats['by_zona'].iterrows():
                    zona_data.append([f"Zona {row['zona']}", str(row['count'])])
                
                zona_table = Table(zona_data)
                zona_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(zona_table)
                story.append(Spacer(1, 15))
            
            # Estadísticas por sistema
            if 'by_sistema' in stats and not stats['by_sistema'].empty:
                story.append(Paragraph("Participantes por Sistema", self.styles['Heading3']))
                sistema_data = []
                for _, row in stats['by_sistema'].iterrows():
                    sistema_data.append([f"Sistema {row['sistema']}", str(row['count'])])
                
                sistema_table = Table(sistema_data)
                sistema_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(sistema_table)
                story.append(Spacer(1, 20))
            
            # Ranking estadístico
            story.append(Paragraph("Ranking Estadístico", self.styles['Heading2']))
            ranking_data = []
            
            # Zona más reportada
            if 'top_zona' in stats:
                ranking_data.append(['Zona más reportada', f"{stats['top_zona']['zona']} ({stats['top_zona']['count']} reportes)"])
            
            # Sistema más reportado
            if 'top_sistema' in stats:
                ranking_data.append(['Sistema más reportado', f"{stats['top_sistema']['sistema']} ({stats['top_sistema']['count']} reportes)"])
            
            # Indicativo más reportado
            if 'top_call_sign' in stats:
                ranking_data.append(['Indicativo más reportado', f"{stats['top_call_sign']['call_sign']} ({stats['top_call_sign']['count']} reportes)"])
            
            if ranking_data:
                ranking_table = Table(ranking_data)
                ranking_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(ranking_table)
                story.append(Spacer(1, 20))
        
        # Tabla de reportes
        if not df.empty:
            story.append(Paragraph("Reportes Registrados", self.styles['Heading2']))
            
            # Preparar datos para la tabla (sin columna Región)
            headers = ['Indicativo', 'Operador', 'Estado', 'Ciudad', 'Señal', 'Zona', 'Sistema', 'Observaciones', 'Fecha/Hora']
            export_data = []
            for _, row in df.iterrows():
                export_data.append({
                    'Indicativo': row['call_sign'],
                    'Operador': row['operator_name'],
                    'Estado': row.get('estado', 'N/A'),
                    'Ciudad': row.get('ciudad', row.get('qth', 'N/A')),  # Fallback to qth for old data
                    'Señal': row['signal_report'],
                    'Zona': row['zona'],
                    'Sistema': row['sistema'],
                    'Observaciones': row['observations'],
                    'Fecha/Hora': pd.to_datetime(row['timestamp']).strftime('%d/%m/%Y %H:%M')
                })
            
            # Crear tabla
            table = Table([headers] + [list(row.values()) for row in export_data], repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
        
        # Construir PDF
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue(), filename
    
    def create_session_summary(self, stats, session_date=None):
        """Crea un resumen de sesión"""
        summary = {
            'fecha_sesion': session_date or datetime.now().date(),
            'total_participantes': stats.get('total_participants', 0),
            'total_reportes': stats.get('total_reports', 0),
            'participantes_por_region': {},
            'calidad_señal': {}
        }
        
        # Procesar participantes por región
        if 'by_region' in stats and not stats['by_region'].empty:
            for _, row in stats['by_region'].iterrows():
                summary['participantes_por_region'][row['region']] = row['count']
        
        # Procesar participantes por zona
        summary['participantes_por_zona'] = {}
        if 'by_zona' in stats and not stats['by_zona'].empty:
            for _, row in stats['by_zona'].iterrows():
                summary['participantes_por_zona'][row['zona']] = row['count']
        
        # Procesar participantes por sistema
        summary['participantes_por_sistema'] = {}
        if 'by_sistema' in stats and not stats['by_sistema'].empty:
            for _, row in stats['by_sistema'].iterrows():
                summary['participantes_por_sistema'][row['sistema']] = row['count']
        
        # Procesar calidad de señal
        if 'signal_quality' in stats and not stats['signal_quality'].empty:
            total_signals = stats['signal_quality']['count'].sum()
            for _, row in stats['signal_quality'].iterrows():
                quality_text = {1: 'Mala', 2: 'Regular', 3: 'Buena'}.get(row['signal_quality'], 'Desconocida')
                percentage = (row['count'] / total_signals * 100) if total_signals > 0 else 0
                summary['calidad_señal'][quality_text] = {
                    'cantidad': row['count'],
                    'porcentaje': round(percentage, 1)
                }
        
        return summary
    
    def get_download_link(self, data, filename, file_type='csv'):
        """Genera enlace de descarga para Streamlit"""
        if file_type == 'csv':
            mime_type = 'text/csv'
        elif file_type == 'xlsx':
            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif file_type == 'pdf':
            mime_type = 'application/pdf'
        else:
            mime_type = 'application/octet-stream'
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        b64 = base64.b64encode(data).decode()
        return f'<a href="data:{mime_type};base64,{b64}" download="{filename}">Descargar {filename}</a>'
