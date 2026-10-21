\begin{table}[htbp]
\centering
\caption{Matriz de escenarios sint{\'{e}}ticos simulados, puntuaciones normalizadas, c{\'{a}}lculo del {\'{I}}ndice $R$ (\%) y clasificaci{\'{o}}n esperada de riesgo.}
\label{tab:30_casos_simulados}
\resizebox{\textwidth}{!}{%
\begin{tabular}{cccccccccc}
\toprule
\textbf{ID Caso} & \textbf{\begin{tabular}[c]{@{}c@{}}Edad\\ (a{\~{n}}os)\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}BLL\\ ($\mu\text{g/dL}$)\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}Hb\\ ($\text{g/dL}$)*\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}Residencia\\ (a{\~{n}}os)\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}Cercan{\'{i}}a\\ ($<1\text{km}$)\end{tabular}} & \textbf{Antecedente} & \textbf{Vector Normalizado ($S_{\text{BLL}}, S_{\text{Hb}}, S_{\text{edad}}, S_{\text{cerc}}, S_{\text{res}}, S_{\text{antec}}$)} & \textbf{{\'{I}}ndice $R$ (\%)} & \textbf{Clasificaci{\'{o}}n Esperada} \\ \midrule
\textbf{C01} & $8$ & $1.2$ & $13.5$ & $1$ & No & No & $(0.00, 0.00, 0.00, 0.00, 0.00, 0.00)$ & $0.0\%$ & \textbf{Riesgo Bajo} \\
\textbf{C02} & $6$ & $2.0$ & $12.8$ & $2$ & No & No & $(0.00, 0.00, 0.00, 0.00, 0.00, 0.00)$ & $0.0\%$ & \textbf{Riesgo Bajo} \\
\textbf{C03} & $4$ & $1.5$ & $12.5$ & $1$ & No & No & $(0.00, 0.00, 1.00, 0.00, 0.00, 0.00)$ & $15.0\%$ & \textbf{Riesgo Bajo} \\
\textbf{C04} & $7$ & $3.8$ & $13.0$ & $2$ & No & No & $(0.33, 0.00, 0.00, 0.00, 0.00, 0.00)$ & $10.0\%$ & \textbf{Riesgo Bajo} \\
\textbf{C05} & $3$ & $2.5$ & $12.2$ & $1$ & No & S{\'{i}} & $(0.00, 0.00, 1.00, 0.00, 0.00, 1.00)$ & $25.0\%$ & \textbf{Riesgo Bajo} \\
\textbf{C06} & $9$ & $1.8$ & $11.5$ & $2$ & No & No & $(0.00, 0.50, 0.00, 0.00, 0.00, 0.00)$ & $10.0\%$ & \textbf{Riesgo Bajo} \\
\textbf{C07} & $5$ & $3.2$ & $12.6$ & $2$ & No & No & $(0.00, 0.00, 1.00, 0.00, 0.00, 0.00)$ & $15.0\%$ & \textbf{Riesgo Bajo} \\
\textbf{C08} & $10$ & $4.2$ & $12.5$ & $4$ & No & No & $(0.33, 0.00, 0.00, 0.00, 1.00, 0.00)$ & $20.0\%$ & \textbf{Riesgo Bajo} \\
\textbf{C09} & $6$ & $2.8$ & $13.0$ & $1$ & S{\'{i}} & No & $(0.00, 0.00, 0.00, 1.00, 0.00, 0.00)$ & $15.0\%$ & \textbf{Riesgo Bajo} \\
\textbf{C10} & $4$ & $3.0$ & $12.1$ & $2$ & No & S{\'{i}} & $(0.00, 0.00, 1.00, 0.00, 0.00, 1.00)$ & $25.0\%$ & \textbf{Riesgo Bajo} \\ \cmidrule(lr){1-10}
\textbf{C11} & $4$ & $4.5$ & $12.0$ & $3$ & No & S{\'{i}} & $(0.33, 0.00, 1.00, 0.00, 1.00, 1.00)$ & $45.0\%$ & \textbf{Riesgo Moderado} \\
\textbf{C12} & $5$ & $6.2$ & $12.5$ & $2$ & No & No & $(0.67, 0.00, 1.00, 0.00, 0.00, 0.00)$ & $35.0\%$ & \textbf{Riesgo Moderado} \\
\textbf{C13} & $7$ & $5.5$ & $11.2$ & $4$ & S{\'{i}} & No & $(0.67, 0.50, 0.00, 1.00, 1.00, 0.00)$ & $55.0\%$ & \textbf{Riesgo Moderado} \\
\textbf{C14} & $3$ & $3.8$ & $11.5$ & $2$ & S{\'{i}} & S{\'{i}} & $(0.33, 0.50, 1.00, 1.00, 0.00, 1.00)$ & $60.0\%$ & \textbf{Riesgo Moderado} \\
\textbf{C15} & $8$ & $7.5$ & $12.8$ & $5$ & No & S{\'{i}} & $(0.67, 0.00, 0.00, 0.00, 1.00, 1.00)$ & $40.0\%$ & \textbf{Riesgo Moderado} \\
\textbf{C16} & $4$ & $5.2$ & $12.4$ & $1$ & S{\'{i}} & No & $(0.67, 0.00, 1.00, 1.00, 0.00, 0.00)$ & $50.0\%$ & \textbf{Riesgo Moderado} \\
\textbf{C17} & $6$ & $8.0$ & $11.4$ & $3$ & No & No & $(0.67, 0.50, 0.00, 0.00, 1.00, 0.00)$ & $40.0\%$ & \textbf{Riesgo Moderado} \\
\textbf{C18} & $2$ & $4.0$ & $11.8$ & $2$ & No & S{\'{i}} & $(0.33, 0.50, 1.00, 0.00, 0.00, 1.00)$ & $45.0\%$ & \textbf{Riesgo Moderado} \\
\textbf{C19} & $5$ & $6.8$ & $12.1$ & $3$ & S{\'{i}} & No & $(0.67, 0.00, 1.00, 1.00, 1.00, 0.00)$ & $60.0\%$ & \textbf{Riesgo Moderado} \\
\textbf{C20} & $9$ & $6.0$ & $10.8$ & $4$ & No & S{\'{i}} & $(0.67, 1.00, 0.00, 0.00, 1.00, 1.00)$ & $60.0\%$ & \textbf{Riesgo Moderado} \\ \cmidrule(lr){1-10}
\textbf{C21} & $3$ & $11.5$ & $10.5$ & $3$ & S{\'{i}} & S{\'{i}} & $(1.00, 1.00, 1.00, 1.00, 1.00, 1.00)$ & $100.0\%$ & \textbf{Riesgo Alto} \\
\textbf{C22} & $4$ & $10.2$ & $11.4$ & $3$ & S{\'{i}} & No & $(1.00, 0.50, 1.00, 1.00, 1.00, 0.00)$ & $80.0\%$ & \textbf{Riesgo Alto} \\
\textbf{C23} & $5$ & $8.5$ & $10.2$ & $4$ & S{\'{i}} & S{\'{i}} & $(0.67, 1.00, 1.00, 1.00, 1.00, 1.00)$ & $85.0\%$ & \textbf{Riesgo Alto} \\
\textbf{C24} & $2$ & $12.0$ & $11.0$ & $2$ & S{\'{i}} & S{\'{i}} & $(1.00, 0.50, 1.00, 1.00, 0.00, 1.00)$ & $80.0\%$ & \textbf{Riesgo Alto} \\
\textbf{C25} & $4$ & $10.8$ & $12.2$ & $4$ & S{\'{i}} & S{\'{i}} & $(1.00, 0.00, 1.00, 1.00, 1.00, 1.00)$ & $80.0\%$ & \textbf{Riesgo Alto} \\
\textbf{C26} & $3$ & $7.8$ & $10.4$ & $3$ & S{\'{i}} & S{\'{i}} & $(0.67, 1.00, 1.00, 1.00, 1.00, 1.00)$ & $85.0\%$ & \textbf{Riesgo Alto} \\
\textbf{C27} & $6$ & $14.0$ & $10.8$ & $5$ & S{\'{i}} & No & $(1.00, 1.00, 0.00, 1.00, 1.00, 0.00)$ & $75.0\%$ & \textbf{Riesgo Alto} \\
\textbf{C28} & $4$ & $11.0$ & $11.8$ & $3$ & S{\'{i}} & S{\'{i}} & $(1.00, 0.50, 1.00, 1.00, 1.00, 1.00)$ & $90.0\%$ & \textbf{Riesgo Alto} \\
\textbf{C29} & $5$ & $9.2$ & $10.5$ & $4$ & S{\'{i}} & No & $(0.67, 1.00, 1.00, 1.00, 1.00, 0.00)$ & $75.0\%$ & \textbf{Riesgo Alto} \\
\textbf{C30} & $3$ & $12.5$ & $12.5$ & $2$ & S{\'{i}} & S{\'{i}} & $(1.00, 0.00, 1.00, 1.00, 0.00, 1.00)$ & $70.0\%$ & \textbf{Riesgo Alto} \\ \bottomrule
\end{tabular}%
}
\end{table}
