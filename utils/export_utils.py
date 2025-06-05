import os
import io
import pandas as pd
from utils.formatting import format_decimal, format_percentage
from utils.i18n import get_text
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, Frame, PageTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def export_to_excel(session_data, is_current=True, st=None):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    # get_text đã import trực tiếp, không lấy từ session_state nữa
    if is_current:
        criteria = st.session_state.criteria
        alternatives = st.session_state.alternatives
        criteria_weights = st.session_state.criteria_weights
        alternative_weights = st.session_state.alternative_weights
        final_scores = st.session_state.final_scores
        consistency_ratios = st.session_state.consistency_ratios
        lambda_max_values = getattr(st.session_state, 'lambda_max_values', None)
        consistency_indices = getattr(st.session_state, 'consistency_indices', None)
    else:
        criteria = session_data['criteria']
        alternatives = session_data['alternatives']
        criteria_weights = session_data['criteria_weights']
        alternative_weights = session_data['alternative_weights']
        final_scores = session_data['final_scores']
        consistency_ratios = session_data['consistency_ratios']
        lambda_max_values = session_data.get('lambda_max_values', None)
        consistency_indices = session_data.get('consistency_indices', None)
    # Create dataframe for criteria weights
    criteria_weights_df = pd.DataFrame({
        get_text("criterion"): criteria,
        get_text("weight"): [format_decimal(w) for w in criteria_weights]
    })
    criteria_weights_df = criteria_weights_df.sort_values(get_text("weight"), ascending=False)
    criteria_weights_df.to_excel(writer, sheet_name=get_text("criteria_weights"), index=False)
    # Create dataframe for consistency metrics
    if lambda_max_values and consistency_indices:
        cr_data = {
            get_text("criterion"): criteria,
            "λ_max": [format_decimal(lambda_max_values[c]) for c in criteria],
            "CI": [format_decimal(consistency_indices[c]) for c in criteria],
            "CR": [format_decimal(consistency_ratios[c]) for c in criteria]
        }
    else:
        cr_data = {
            get_text("criterion"): criteria,
            "CR": [format_decimal(consistency_ratios[c]) for c in criteria]
        }
    cr_df = pd.DataFrame(cr_data)
    cr_df.to_excel(writer, sheet_name=get_text("consistency_metrics"), index=False)
    # Create dataframes for alternative weights by criterion
    for i, criterion in enumerate(criteria):
        alt_weights_df = pd.DataFrame({
            get_text("alternative"): alternatives,
            get_text("weight"): [format_decimal(w) for w in alternative_weights[criterion]]
        })
        alt_weights_df = alt_weights_df.sort_values(get_text("weight"), ascending=False)
        alt_weights_df.to_excel(writer, sheet_name=f"{criterion[:30]}", index=False)
    # Create dataframe for final scores
    final_scores_df = pd.DataFrame({
        get_text("alternative"): alternatives,
        get_text("score"): [format_percentage(s) for s in final_scores]
    })
    final_scores_df = final_scores_df.sort_values(get_text("score"), ascending=False)
    final_scores_df[get_text("rank")] = range(1, len(final_scores_df) + 1)
    final_scores_df.to_excel(writer, sheet_name=get_text("final_scores"), index=False)
    writer.close()
    return output.getvalue()


def export_to_pdf(session_data, is_current=True, st=None, criteria_matrix=None, alternative_matrices=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from datetime import datetime
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
    from reportlab.lib.pagesizes import A4
    
    buffer = io.BytesIO()
    # get_text đã import trực tiếp, không lấy từ session_state nữa
    if is_current:
        criteria = st.session_state.criteria
        alternatives = st.session_state.alternatives
        criteria_weights = st.session_state.criteria_weights
        alternative_weights = st.session_state.alternative_weights
        final_scores = st.session_state.final_scores
        consistency_ratios = st.session_state.consistency_ratios
        lambda_max_values = getattr(st.session_state, 'lambda_max_values', None)
        consistency_indices = getattr(st.session_state, 'consistency_indices', None)
        report_title = getattr(st.session_state, 'current_session_name', "Kết quả AHP")
        report_desc = getattr(st.session_state, 'current_session_description', "")
        report_time = datetime.now().strftime('%d/%m/%Y %H:%M')
        # Lấy ma trận đầu vào nếu chưa truyền vào
        if criteria_matrix is None:
            criteria_matrix = st.session_state.criteria_matrix
        if alternative_matrices is None:
            alternative_matrices = st.session_state.alternative_matrices
    else:
        criteria = session_data['criteria']
        alternatives = session_data['alternatives']
        criteria_weights = session_data['criteria_weights']
        alternative_weights = session_data['alternative_weights']
        final_scores = session_data['final_scores']
        consistency_ratios = session_data['consistency_ratios']
        lambda_max_values = session_data.get('lambda_max_values', None)
        consistency_indices = session_data.get('consistency_indices', None)
        report_title = session_data.get('name', "Kết quả AHP")
        report_desc = session_data.get('description', "")
        report_time = session_data.get('timestamp', datetime.now().strftime('%d/%m/%Y %H:%M'))
        # Lấy ma trận đầu vào nếu có (ưu tiên dạng list để in ra PDF)
        if criteria_matrix is None:
            if 'criteria_matrix_list' in session_data:
                criteria_matrix = session_data['criteria_matrix_list']
            else:
                criteria_matrix = session_data.get('criteria_matrix', None)
        if alternative_matrices is None:
            if 'alternative_matrices_list' in session_data:
                alternative_matrices = session_data['alternative_matrices_list']
            else:
                alternative_matrices = session_data.get('alternative_matrices', None)
    # Font đẹp cho tiếng Việt (nếu có)
    font_name = 'Helvetica'
    bold_font_name = 'Helvetica-Bold'
    font_error = None
    font_candidates = [
        ('Roboto', 'Roboto-Regular.ttf', 'Roboto-Bold.ttf'),
        ('DejaVuSans', 'DejaVuSans.ttf', 'DejaVuSans-Bold.ttf')
    ]
    for name, regular, bold in font_candidates:
        if os.path.exists(regular) and os.path.exists(bold):
            try:
                pdfmetrics.registerFont(TTFont(name, regular))
                pdfmetrics.registerFont(TTFont(f"{name}-Bold", bold))
                font_name = name
                bold_font_name = f"{name}-Bold"
                break
            except Exception as e:
                font_error = f"Không thể đăng ký font {name}: {e}"
    else:
        if not font_error:
            font_error = "Không tìm thấy file font Roboto hoặc DejaVuSans trong thư mục dự án. PDF sẽ dùng font mặc định (không hỗ trợ tiếng Việt)."
    styles = getSampleStyleSheet()
    # Định nghĩa lại lề PDF
    left_margin = 3*cm
    right_margin = 2*cm
    top_margin = 2*cm
    bottom_margin = 2*cm
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=right_margin, leftMargin=left_margin, topMargin=top_margin, bottomMargin=bottom_margin)
    # Định nghĩa lại style
    title_style = ParagraphStyle('Title', fontName=bold_font_name, fontSize=15, alignment=TA_CENTER, spaceAfter=20, textColor=colors.HexColor('#003366'))
    subtitle_style = ParagraphStyle('Subtitle', fontName=font_name, fontSize=14, alignment=TA_CENTER, spaceAfter=10, textColor=colors.HexColor('#005B96'))
    heading_style = ParagraphStyle('Heading', fontName=bold_font_name, fontSize=15, alignment=TA_CENTER, spaceAfter=8, textColor=colors.HexColor('#003366'))
    normal_style = ParagraphStyle('Normal', fontName=font_name, fontSize=13, alignment=4, spaceAfter=6)  # 4 = justify
    table_header_style = ParagraphStyle('TableHeader', fontName=bold_font_name, fontSize=13, alignment=TA_CENTER, textColor=colors.white)
    # Header/footer
    def header_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(font_name, 9)
        canvas.setFillColor(colors.HexColor('#003366'))
        canvas.drawString(doc.leftMargin, A4[1] - 20, f"AHP - {report_title}")
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(A4[0] - doc.rightMargin, 20, f"Trang {doc.page}")
        canvas.restoreState()
    
    elements = []
    elements = []
    # Thông báo lỗi font nếu có
    if font_error:
        elements.append(Paragraph(f"<font color='red'><b>LỖI FONT:</b> {font_error}</font>", normal_style))
        elements.append(Spacer(1, 0.2*cm))
    # Section: Tiêu đề & mô tả
    elements.append(Paragraph(report_title, title_style))
    if report_desc:
        elements.append(Paragraph(report_desc, subtitle_style))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(f"<b>Ngày:</b> {report_time}", normal_style))
    elements.append(Spacer(1, 0.5*cm))
    # Section: Tổng quan
    # elements.append(Paragraph("<b>Phân tích</b>", heading_style))
    # elements.append(Paragraph(f"<b>Tên phân tích:</b> {report_title}", normal_style))
    # if report_desc:
    #     elements.append(Paragraph(f"<b>Mô tả:</b> {report_desc}", normal_style))
    # elements.append(Paragraph(f"<b>Số tiêu chí:</b> {len(criteria)}", normal_style))
    # elements.append(Paragraph(f"<b>Số phương án:</b> {len(alternatives)}", normal_style))
    # Danh sách tiêu chí
    elements.append(Paragraph("<b>Danh sách tiêu chí:</b>", heading_style))
    for c in criteria:
        elements.append(Paragraph(f"- {c}", normal_style))
    # Danh sách phương án
    elements.append(Paragraph("<b>Danh sách phương án:</b>", heading_style))
    for a in alternatives:
        elements.append(Paragraph(f"- {a}", normal_style))
    elements.append(Spacer(1, 0.5*cm))
    # Section: Bảng so sánh các cặp tiêu chí và trọng số tiêu chí
    elements.append(Paragraph("<b>Bảng so sánh các cặp tiêu chí</b>", heading_style))
    if criteria_matrix is not None:
        # Header: thêm ô trống đầu, sau đó là tên các tiêu chí
        matrix_header = [Paragraph("", table_header_style)] + [Paragraph(c, table_header_style) for c in criteria]
        matrix_data = [matrix_header]
        for i, row in enumerate(criteria_matrix):
            matrix_data.append([
                Paragraph(criteria[i], table_header_style)
            ] + [Paragraph(format_decimal(cell), normal_style) for cell in row])
        matrix_table = Table(matrix_data, colWidths=[doc.width/(len(criteria)+0.5)]*(len(criteria)+1))
        matrix_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#005B96')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), bold_font_name),
            ('FONTNAME', (0, 1), (0, -1), bold_font_name),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#005B96')),
            ('TEXTCOLOR', (0, 1), (0, -1), colors.white),
            ('BACKGROUND', (1, 1), (-1, -1), colors.HexColor('#F4F4F9')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#005B96')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        elements.append(matrix_table)
        elements.append(Spacer(1, 0.2*cm))
        # Bảng trọng số tiêu chí
        elements.append(Paragraph("<b>Bảng trọng số tiêu chí</b>", heading_style))
        criteria_weights_data = [[Paragraph(get_text("criterion"), table_header_style), Paragraph(get_text("weight"), table_header_style)]]
        for i, c in enumerate(criteria):
            criteria_weights_data.append([Paragraph(c, normal_style), Paragraph(format_decimal(criteria_weights[i]), normal_style)])
        criteria_weights_table = Table(criteria_weights_data, colWidths=[doc.width*0.7, doc.width*0.3])
        criteria_weights_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#005B96')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), bold_font_name),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F4F4F9')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#005B96')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        elements.append(criteria_weights_table)
        elements.append(Spacer(1, 0.2*cm))
        # Bảng chỉ số nhất quán tiêu chí
        elements.append(Paragraph("<b>Bảng chỉ số nhất quán tiêu chí</b>", heading_style))
        if lambda_max_values and consistency_indices:
            consistency_header = [Paragraph(get_text("criterion"), table_header_style), Paragraph("λ_max", table_header_style), Paragraph("CI", table_header_style), Paragraph("CR", table_header_style)]
            consistency_data = [consistency_header]
            for c in criteria:
                consistency_data.append([
                    Paragraph(c, normal_style),
                    Paragraph(format_decimal(lambda_max_values[c]), normal_style),
                    Paragraph(format_decimal(consistency_indices[c]), normal_style),
                    Paragraph(format_decimal(consistency_ratios[c]), normal_style)
                ])
            col_widths = [doc.width*0.4, doc.width*0.2, doc.width*0.2, doc.width*0.2]
        else:
            consistency_header = [Paragraph(get_text("criterion"), table_header_style), Paragraph("CR", table_header_style)]
            consistency_data = [consistency_header]
            for c in criteria:
                consistency_data.append([
                    Paragraph(c, normal_style),
                    Paragraph(format_decimal(consistency_ratios[c]), normal_style)
                ])
            col_widths = [doc.width*0.7, doc.width*0.3]
        consistency_table = Table(consistency_data, colWidths=col_widths)
        consistency_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#005B96')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), bold_font_name),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F4F4F9')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#005B96')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        elements.append(consistency_table)
        elements.append(Spacer(1, 0.5*cm))
    # Section: Bảng so sánh các cặp phương án theo từng tiêu chí
    if alternative_matrices is not None:
        for idx, criterion in enumerate(criteria):
            elements.append(Paragraph(f"<b>Bảng so sánh các cặp phương án theo tiêu chí: {criterion}</b>", heading_style))
            # Header: thêm ô trống đầu, sau đó là tên các phương án
            alt_header = [Paragraph("", table_header_style)] + [Paragraph(a, table_header_style) for a in alternatives]
            alt_matrix = alternative_matrices[criterion] if isinstance(alternative_matrices, dict) else alternative_matrices[idx]
            alt_matrix_data = [alt_header]
            for i, row in enumerate(alt_matrix):
                alt_matrix_data.append([
                    Paragraph(alternatives[i], table_header_style)
                ] + [Paragraph(format_decimal(cell), normal_style) for cell in row])
            alt_matrix_table = Table(alt_matrix_data, colWidths=[doc.width/(len(alternatives)+0.5)]*(len(alternatives)+1))
            alt_matrix_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6497B1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), bold_font_name),
                ('FONTNAME', (0, 1), (0, -1), bold_font_name),
                ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#6497B1')),
                ('TEXTCOLOR', (0, 1), (0, -1), colors.white),
                ('BACKGROUND', (1, 1), (-1, -1), colors.HexColor('#F4F4F9')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#6497B1')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            elements.append(alt_matrix_table)
            elements.append(Spacer(1, 0.2*cm))
            # Bảng trọng số phương án theo tiêu chí
            elements.append(Paragraph(f"<b>Bảng trọng số phương án theo tiêu chí: {criterion}</b>", heading_style))
            alt_weights = alternative_weights[criterion]
            alt_indices = pd.Series(alt_weights).sort_values(ascending=False).index
            alt_data = [[Paragraph(get_text("alternative"), table_header_style), Paragraph(get_text("weight"), table_header_style)]]
            for idx2 in alt_indices:
                alt_data.append([Paragraph(alternatives[idx2], normal_style), Paragraph(format_decimal(alt_weights[idx2]), normal_style)])
            alt_table = Table(alt_data, colWidths=[doc.width*0.7, doc.width*0.3])
            alt_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6497B1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), bold_font_name),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F4F4F9')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#6497B1')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            elements.append(alt_table)
            # Bảng chỉ số nhất quán phương án theo tiêu chí
            if lambda_max_values and consistency_indices and criterion in lambda_max_values and criterion in consistency_indices and criterion in consistency_ratios:
                elements.append(Spacer(1, 0.1*cm))
                elements.append(Paragraph(f"<b>Bảng chỉ số nhất quán phương án theo tiêu chí: {criterion}</b>", heading_style))
                sub_consistency_data = [
                    [Paragraph("λ_max", table_header_style), Paragraph("CI", table_header_style), Paragraph("CR", table_header_style)],
                    [
                        Paragraph(format_decimal(lambda_max_values[criterion]), normal_style),
                        Paragraph(format_decimal(consistency_indices[criterion]), normal_style),
                        Paragraph(format_decimal(consistency_ratios[criterion]), normal_style)
                    ]
                ]
                sub_consistency_table = Table(sub_consistency_data, colWidths=[doc.width*0.25]*3)
                sub_consistency_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#b3cde0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), bold_font_name),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F4F4F9')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#b3cde0')),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                ]))
                elements.append(sub_consistency_table)
            elements.append(Spacer(1, 0.4*cm))
    # Section: Kết quả cuối cùng và xếp hạng
    elements.append(Paragraph("<b>Kết quả cuối cùng và xếp hạng</b>", heading_style))
    sorted_indices = pd.Series(final_scores).sort_values(ascending=False).index
    final_scores_data = [[Paragraph(get_text("rank"), table_header_style), Paragraph(get_text("alternative"), table_header_style), Paragraph(get_text("score"), table_header_style)]]
    for i, idx in enumerate(sorted_indices):
        final_scores_data.append([Paragraph(str(i+1), normal_style), Paragraph(alternatives[idx], normal_style), Paragraph(format_percentage(final_scores[idx]), normal_style)])
    final_scores_table = Table(final_scores_data, colWidths=[doc.width*0.1, doc.width*0.6, doc.width*0.3])
    final_scores_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#005B96')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font_name),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F4F4F9')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#005B96')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    elements.append(final_scores_table)
    elements.append(Spacer(1, 0.5*cm))
    # Section: Biểu đồ
    elements.append(Paragraph("<b>Biểu đồ kết quả</b>", heading_style))
    try:
        sorted_alternatives = [alternatives[i] for i in sorted_indices]
        sorted_scores = [final_scores[i] for i in sorted_indices]
        plt.figure(figsize=(7, 5))
        plt.barh(sorted_alternatives, sorted_scores, color='#005B96')
        plt.xlabel(get_text("score"), fontsize=12)
        plt.ylabel(get_text("alternative"), fontsize=12)
        plt.title(get_text("final_scores"), fontsize=14)
        plt.tight_layout()
        chart_buffer = io.BytesIO()
        plt.savefig(chart_buffer, format='png', dpi=300, bbox_inches='tight')
        chart_buffer.seek(0)
        img = Image(chart_buffer, width=doc.width, height=3*inch)
        elements.append(img)
        plt.close()
    except Exception as e:
        elements.append(Paragraph(f"Không thể tạo biểu đồ. Lỗi: {str(e)}", normal_style))
    # Build PDF
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    buffer.seek(0)
    return buffer.getvalue()
