from datetime import date

import plotly.express as px
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from winter.modules.database import get_session, WeightEntry


def main():
    st.title("📊 Seguimiento de Peso")

    # Formulario para ingresar el peso
    with st.form("weight_form"):
        weight = st.number_input("Ingresa tu peso (kg):", min_value=0.0, max_value=500.0, step=0.1)
        entry_date = st.date_input("Fecha:", value=date.today())
        submit = st.form_submit_button("Guardar")

    if submit:
        if weight > 0:
            session = get_session()
            new_entry = WeightEntry(
                user_id=st.session_state['user_id'],
                date=entry_date,
                weight=weight
            )
            session.add(new_entry)
            try:
                session.commit()
                st.success("Registro de peso guardado correctamente.")
            except SQLAlchemyError as e:
                session.rollback()
                st.error(f"Error al guardar el registro: {e}")
            finally:
                session.close()
        else:
            st.error("Por favor, ingresa un peso válido.")

    # Recuperar y mostrar los registros de peso
    session = get_session()
    entries = session.query(WeightEntry).filter(
        WeightEntry.user_id == st.session_state['user_id']
    ).order_by(WeightEntry.date).all()
    session.close()

    if entries:
        # Preparar datos para el gráfico
        dates = [entry.date for entry in entries]
        weights = [entry.weight for entry in entries]

        # Crear dos columnas para los controles
        col1, col2 = st.columns(2)

        with col1:
            # Selector de rango de fechas
            st.subheader("Rango de Fechas")
            start_date = st.date_input("Fecha de inicio:", value=min(dates), key="start_date")
            end_date = st.date_input("Fecha de fin:", value=max(dates), key="end_date")

        with col2:
            # Selector de peso objetivo
            st.subheader("Peso Objetivo")
            target_weight = st.number_input(
                "Peso objetivo (kg):",
                min_value=0.0,
                max_value=500.0,
                step=0.1,
                key="target_weight"
            )

        if start_date > end_date:
            st.error("La fecha de inicio no puede ser posterior a la fecha de fin.")
        else:
            # Filtrar datos según el rango seleccionado
            filtered_data = [(d, w) for d, w in zip(dates, weights) if start_date <= d <= end_date]

            if filtered_data:
                filtered_dates, filtered_weights = zip(*filtered_data)

                # Crear y mostrar el gráfico
                fig = px.line(
                    x=filtered_dates,
                    y=filtered_weights,
                    labels={'x': 'Fecha', 'y': 'Peso (kg)'},
                    title='Progreso de Peso'
                )

                # Agregar línea horizontal para el peso objetivo si se ha establecido
                if target_weight > 0:
                    fig.add_hline(
                        y=target_weight,
                        line_dash="dash",
                        line_color="red",
                        annotation_text="Objetivo",
                        annotation_position="right"
                    )

                st.plotly_chart(fig)
            else:
                st.warning("No hay datos para el rango de fechas seleccionado.")
    else:
        st.info("Aún no has ingresado registros de peso.")


if __name__ == "__main__":
    main()
