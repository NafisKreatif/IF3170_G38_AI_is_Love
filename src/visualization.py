from html import escape
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots


PACKAGE_COLORS = (
    "#4C78A8",
    "#F58518",
    "#54A24B",
    "#E45756",
    "#72B7B2",
    "#B279A2",
    "#FF9DA6",
    "#9D755D",
    "#BAB0AC",
)


def _box_mesh(x, y, z, width, length, height, color, *, name, hovertext=None):
    vertices = (
        (x, y, z),
        (x + width, y, z),
        (x + width, y + length, z),
        (x, y + length, z),
        (x, y, z + height),
        (x + width, y, z + height),
        (x + width, y + length, z + height),
        (x, y + length, z + height),
    )
    faces = (
        (0, 1, 2), (0, 2, 3),
        (4, 6, 5), (4, 7, 6),
        (0, 4, 5), (0, 5, 1),
        (1, 5, 6), (1, 6, 2),
        (2, 6, 7), (2, 7, 3),
        (3, 7, 4), (3, 4, 0),
    )
    return go.Mesh3d(
        x=[point[0] for point in vertices],
        y=[point[1] for point in vertices],
        z=[point[2] for point in vertices],
        i=[face[0] for face in faces],
        j=[face[1] for face in faces],
        k=[face[2] for face in faces],
        color=color,
        opacity=1,
        flatshading=False,
        lighting={
            "ambient": 1,
            "diffuse": 0,
            "specular": 0,
            "roughness": 1,
            "fresnel": 0,
        },
        lightposition={"x": 100, "y": 150, "z": 100},
        name=name,
        hovertext=hovertext,
        hoverinfo="text" if hovertext else "name",
        showlegend=False,
    )


def _truck_wireframe(truck, x_offset):
    width = truck.dimensions.width
    length = truck.dimensions.length
    height = truck.dimensions.height
    corners = (
        (x_offset, 0, 0),
        (x_offset + width, 0, 0),
        (x_offset + width, length, 0),
        (x_offset, length, 0),
        (x_offset, 0, height),
        (x_offset + width, 0, height),
        (x_offset + width, length, height),
        (x_offset, length, height),
    )
    edges = (
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    )
    x_values, y_values, z_values = [], [], []
    for start, end in edges:
        x_values.extend((corners[start][0], corners[end][0], None))
        y_values.extend((corners[start][1], corners[end][1], None))
        z_values.extend((corners[start][2], corners[end][2], None))

    return go.Scatter3d(
        x=x_values,
        y=y_values,
        z=z_values,
        mode="lines",
        line={"color": "#333333", "width": 4},
        name=f"Truck {truck.id}",
        hoverinfo="name",
        showlegend=False,
    )


def _add_configuration(fig, isekai, state, column):
    gap = max((truck.dimensions.width for truck in isekai.trucks), default=1) * 0.2
    x_offset = 0
    x_extent = 0
    y_extent = 0
    z_extent = 0

    for truck in isekai.trucks:
        fig.add_trace(_truck_wireframe(truck, x_offset), row=1, col=column)
        x_extent = max(x_extent, x_offset + truck.dimensions.width)
        y_extent = max(y_extent, truck.dimensions.length)
        z_extent = max(z_extent, truck.dimensions.height)

        for package_index, package in enumerate(isekai.packages):
            if state.get_package_truck(package) is not truck:
                continue

            position = state.get_package_position(package)
            dimensions = state.get_package_dimensions(package)
            hovertext = (
                f"Package: {package.id}<br>"
                f"Value: {package.value}<br>"
                f"Weight: {package.weight}<br>"
                f"Position: ({position.x}, {position.y}, {position.z})<br>"
                f"Size: ({dimensions.width}, {dimensions.height}, {dimensions.length})"
            )
            fig.add_trace(
                _box_mesh(
                    x_offset + position.x,
                    position.z,
                    position.y,
                    dimensions.width,
                    dimensions.length,
                    dimensions.height,
                    PACKAGE_COLORS[package_index % len(PACKAGE_COLORS)],
                    name=package.id,
                    hovertext=hovertext,
                ),
                row=1,
                col=column,
            )
            x_extent = max(x_extent, x_offset + position.x + dimensions.width)
            y_extent = max(y_extent, position.z + dimensions.length)
            z_extent = max(z_extent, position.y + dimensions.height)

        x_offset += truck.dimensions.width + gap

    return max(x_extent, 1), max(y_extent, 1), max(z_extent, 1)


def _package_details(isekai, state):
    """Build readable package-placement details grouped by truck."""
    sections = []
    for truck in isekai.trucks:
        packages = []
        for package in isekai.packages:
            if state.get_package_truck(package) is not truck:
                continue
            position = state.get_package_position(package)
            dimensions = state.get_package_dimensions(package)
            packages.append(
                "<li>"
                f"<strong>{escape(str(package.id))}</strong> — "
                f"posisi ({position.x}, {position.y}, {position.z}); "
                f"ukuran ({dimensions.width} × {dimensions.height} × {dimensions.length}); "
                f"nilai {package.value}, berat {package.weight}"
                "</li>"
            )
        package_list = "<ul>" + "".join(packages) + "</ul>" if packages else "<p>Tidak ada paket.</p>"
        sections.append(
            f"<section><h4>Truk {escape(str(truck.id))}</h4>{package_list}</section>"
        )
    return "".join(sections)


def _summary_html(run_summary, isekai, initial_state, final_state):
    """Render run statistics and package placements as an HTML section."""
    stats = ""
    if run_summary:
        stats_items = (
            ("Algoritma", run_summary.get("algorithm", "—")),
            ("Nilai awal", run_summary.get("initial_value", "—")),
            ("Nilai akhir", run_summary.get("final_value", "—")),
            ("State akhir valid", "Ya" if final_state.is_valid() else "Tidak"),
            ("Iterasi/generasi", run_summary.get("iterations", "—")),
            ("Durasi", f"{run_summary.get('duration', 0):.3f} detik"),
        )
        stats = "<dl class='stats'>" + "".join(
            f"<div><dt>{escape(str(label))}</dt><dd>{escape(str(value))}</dd></div>"
            for label, value in stats_items
        ) + "</dl>"

    initial_details = _package_details(isekai, initial_state)
    final_details = _package_details(isekai, final_state)
    return f"""
    <section class="report">
      <h2>Ringkasan hasil</h2>
      {stats}
      <div class="placements">
        <article><h3>State awal</h3>{initial_details}</article>
        <article><h3>State akhir</h3>{final_details}</article>
      </div>
    </section>
    """


def save_state_comparison(
    isekai, initial_state, final_state, output_path, run_summary=None
) -> Path:
    """Save interactive initial/final views with a textual run report."""
    output_path = Path(output_path)
    figure = make_subplots(rows=1, cols=1, specs=[[{"type": "scene"}]])

    initial_start = len(figure.data)
    initial_extent = _add_configuration(figure, isekai, initial_state, column=1)
    initial_end = len(figure.data)
    final_start = len(figure.data)
    final_extent = _add_configuration(figure, isekai, final_state, column=1)
    final_end = len(figure.data)
    extent = tuple(max(initial, final) for initial, final in zip(initial_extent, final_extent))

    initial_visibility = [
        initial_start <= index < initial_end for index in range(len(figure.data))
    ]
    final_visibility = [
        final_start <= index < final_end for index in range(len(figure.data))
    ]
    for trace, is_initial in zip(figure.data, initial_visibility):
        trace.visible = is_initial

    scene = {
        "xaxis": {"title": "Width", "range": [0, extent[0]], "showbackground": True},
        "yaxis": {"title": "Length", "range": [0, extent[1]], "showbackground": True},
        "zaxis": {"title": "Height", "range": [0, extent[2]], "showbackground": True},
        "aspectmode": "data",
        "camera": {"eye": {"x": 1.6, "y": 1.4, "z": 1.6}},
    }
    figure.update_layout(
        title="Initial state",
        scene=scene,
        height=680,
        margin={"l": 0, "r": 0, "t": 100, "b": 0},
        updatemenus=[
            {
                "type": "dropdown",
                "direction": "down",
                "x": 0.02,
                "y": 1.12,
                "xanchor": "left",
                "yanchor": "top",
                "buttons": [
                    {
                        "label": "Initial state",
                        "method": "update",
                        "args": [
                            {"visible": initial_visibility},
                            {"title": "Initial state"},
                        ],
                    },
                    {
                        "label": "Final state",
                        "method": "update",
                        "args": [
                            {"visible": final_visibility},
                            {"title": "Final state"},
                        ],
                    },
                ],
            }
        ],
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plot_html = figure.to_html(full_html=False, include_plotlyjs=True)
    report_html = _summary_html(run_summary, isekai, initial_state, final_state)
    page = f"""<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Truck package arrangement</title>
  <style>
    body {{ margin: 0; padding: 20px; color: #202124; font: 15px Arial, sans-serif; background: #f5f7fa; }}
    main {{ max-width: 1500px; margin: auto; }}
    .report {{ padding: 20px; margin-top: 16px; background: white; border: 1px solid #d8dee8; border-radius: 10px; }}
    .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }}
    .stats div, .placements article {{ padding: 12px; background: #f5f7fa; border-radius: 7px; }}
    dt {{ color: #5f6368; font-size: 13px; }} dd {{ margin: 5px 0 0; font-size: 18px; font-weight: 600; }}
    .placements {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }}
    .placements h3 {{ margin-top: 0; }}
    .placements section {{ border-top: 1px solid #d8dee8; padding-top: 4px; }}
    .placements ul {{ padding-left: 20px; }}
    .placements li {{ margin: 7px 0; }}
  </style>
</head>
<body><main>{plot_html}{report_html}</main></body>
</html>"""
    output_path.write_text(page, encoding="utf-8")
    return output_path
