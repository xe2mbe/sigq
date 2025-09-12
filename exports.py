import pandas as pd
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
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
            
            # Reordenar columnas para mejor presentación incluyendo campos HF
            column_order = ['call_sign', 'operator_name', 'qth', 'ciudad', 'zona', 'sistema', 'hf_frequency', 'hf_mode', 'hf_power', 'signal_report', 'grid_locator', 'observations', 'timestamp']
            existing_columns = [col for col in column_order if col in export_df.columns]
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
                    sistema_data.append([f"{row['sistema']}", str(row['count'])])
                
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
        
        # Salto de página para tabla de reportes en orientación horizontal
        if not df.empty:
            story.append(PageBreak())
            
            # Crear nueva página horizontal con encabezado
            current_date = datetime.now().date()
            self._add_landscape_header(story, current_date)
            
            story.append(Paragraph("Reportes Registrados", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Preparar datos para la tabla con campos HF y numeración
            headers = ['#', 'Indicativo', 'Operador', 'Estado', 'Ciudad', 'Zona', 'Sistema', 'Frecuencia', 'Modo', 'Potencia', 'Señal', 'Grid', 'Observaciones', 'Fecha/Hora']
            export_data = []
            for idx, (_, row) in enumerate(df.iterrows(), 1):
                export_data.append([
                    str(idx),  # Número consecutivo
                    row['call_sign'],
                    row['operator_name'],
                    row.get('estado', row.get('qth', 'N/A')),
                    row.get('ciudad', 'N/A'),
                    row['zona'],
                    row['sistema'],
                    row.get('hf_frequency', '-') or '-',
                    row.get('hf_mode', '-') or '-',
                    row.get('hf_power', '-') or '-',
                    row['signal_report'],
                    row.get('grid_locator', 'N/A') or 'N/A',
                    row['observations'] or '-',
                    pd.to_datetime(row['timestamp']).strftime('%d/%m/%Y %H:%M')
                ])
            
            # Crear tabla con ancho optimizado para orientación horizontal
            table = Table([headers] + export_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTSIZE', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            
            story.append(table)
        
        # Construir PDF con orientaciones mixtas
        from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
        from reportlab.platypus.frames import Frame
        
        class MixedOrientationDoc(BaseDocTemplate):
            def __init__(self, filename, **kwargs):
                BaseDocTemplate.__init__(self, filename, **kwargs)
                
                # Template para página vertical (primera página)
                portrait_frame = Frame(0.75*inch, 0.75*inch, 
                                     letter[0] - 1.5*inch, letter[1] - 1.5*inch)
                portrait_template = PageTemplate(id='portrait', frames=[portrait_frame], 
                                               pagesize=letter)
                
                # Template para página horizontal (segunda página)
                landscape_frame = Frame(0.75*inch, 0.75*inch,
                                      landscape(A4)[0] - 1.5*inch, landscape(A4)[1] - 1.5*inch)
                landscape_template = PageTemplate(id='landscape', frames=[landscape_frame],
                                                pagesize=landscape(A4))
                
                self.addPageTemplates([portrait_template, landscape_template])
        
        # Crear documento con orientaciones mixtas
        doc = MixedOrientationDoc(pdf_buffer)
        
        # Separar contenido por páginas
        portrait_story = []
        landscape_story = []
        
        # Primera página (vertical) - todo hasta PageBreak
        page_break_found = False
        for element in story:
            if isinstance(element, PageBreak):
                page_break_found = True
                portrait_story.append(element)
                break
            portrait_story.append(element)
        
        # Segunda página (horizontal) - después del PageBreak
        if page_break_found:
            landscape_found = False
            for element in story:
                if landscape_found:
                    landscape_story.append(element)
                elif isinstance(element, PageBreak):
                    landscape_found = True
        
        # Construir story final con cambios de template
        final_story = []
        
        # Agregar contenido de primera página
        for element in portrait_story:
            if not isinstance(element, PageBreak):
                final_story.append(element)
        
        # Cambiar a template landscape y agregar contenido de segunda página
        if landscape_story:
            from reportlab.platypus import NextPageTemplate
            final_story.append(NextPageTemplate('landscape'))
            final_story.append(PageBreak())
            final_story.extend(landscape_story)
        
        doc.build(final_story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue(), filename
    
    def _add_landscape_header(self, story, session_date):
        """Agrega encabezado para página horizontal"""
        # Logo
        logo_path = "assets/LogoFMRE_medium.png"
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=1*inch, height=1*inch)
            story.append(logo)
        
        # Título y fecha
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=6,
            alignment=1  # Center
        )
        
        story.append(Paragraph("Federación Mexicana de Radio Experimentadores A.C.", title_style))
        story.append(Paragraph(f"Reporte de Sesión - {session_date.strftime('%d/%m/%Y')}", self.styles['Heading3']))
        story.append(Spacer(1, 20))
    
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
