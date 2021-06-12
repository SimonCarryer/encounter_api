import sys
from scipy.spatial import Voronoi, Delaunay
import numpy as np
import random
from copy import copy
from collections import defaultdict

eps = sys.float_info.epsilon


class RegionMapBuilder:
    def __init__(self, relax=0, centralise_points=False):
        self.relax = relax
        self.centralise_points = centralise_points
        # [x_min, x_max, y_min, y_max]
        self.bounding_box = np.array([0., 1., 0., 1.])

    def in_box(self, points):
        return np.logical_and(np.logical_and(self.bounding_box[0] <= points[:, 0],
                                             points[:, 0] <= self.bounding_box[1]),
                              np.logical_and(self.bounding_box[2] <= points[:, 1],
                                             points[:, 1] <= self.bounding_box[3]))

    def reflect_points(self, points):
        i = self.in_box(points)
        points_center = points[i, :]
        points_left = np.copy(points_center)
        points_left[:, 0] = self.bounding_box[0] - \
            (points_left[:, 0] - self.bounding_box[0])
        points_right = np.copy(points_center)
        points_right[:, 0] = self.bounding_box[1] + \
            (self.bounding_box[1] - points_right[:, 0])
        points_down = np.copy(points_center)
        points_down[:, 1] = self.bounding_box[2] - \
            (points_down[:, 1] - self.bounding_box[2])
        points_up = np.copy(points_center)
        points_up[:, 1] = self.bounding_box[3] + \
            (self.bounding_box[3] - points_up[:, 1])
        points = np.append(points_center,
                           np.append(np.append(points_left,
                                               points_right,
                                               axis=0),
                                     np.append(points_down,
                                               points_up,
                                               axis=0),
                                     axis=0),
                           axis=0)
        return points, points_center

    def voronoi(self, points, points_center):
        vor = Voronoi(points)
        vor.filtered_points = points_center
        vor.filtered_regions = [vor.regions[vor.point_region[i]]
                                for i in range(len(points_center))]
        return vor

    def triangles(self, points, points_center):
        tri = Delaunay(points)
        filtered_points = list(range(len(points_center)))
        return [[s if s in filtered_points else -1 for s in simp.tolist()] for simp in tri.simplices if any([point in filtered_points for point in simp])]

    def generate_points(self, n_points):
        if self.centralise_points:
            points = np.random.normal(loc=0.5, scale=0.20, size=[n_points, 2])
        else:
            points = np.random.rand(n_points, 2)
        for _ in range(self.relax):
            points = self.relax_points(points)
        return points

    def centroid_region(self, vertices):
        # Polygon's signed area
        A = 0
        # Centroid's x
        C_x = 0
        # Centroid's y
        C_y = 0
        for i in range(0, len(vertices) - 1):
            s = (vertices[i, 0] * vertices[i + 1, 1] -
                 vertices[i + 1, 0] * vertices[i, 1])
            A = A + s
            C_x = C_x + (vertices[i, 0] + vertices[i + 1, 0]) * s
            C_y = C_y + (vertices[i, 1] + vertices[i + 1, 1]) * s
        A = 0.5 * A
        C_x = (1.0 / (6.0 * A)) * C_x
        C_y = (1.0 / (6.0 * A)) * C_y
        return np.array([C_x, C_y])

    def relax_points(self, points):
        reflected_points, points_center = self.reflect_points(points)
        vor = self.voronoi(reflected_points, points_center)
        boundaries = [vor.vertices[region + [region[0]], :]
                      for region in vor.filtered_regions]
        return np.array([self.centroid_region(boundary) for boundary in boundaries])

    def polygon_area(self, points):
        x = points[:, 0]
        y = points[:, 1]
        return self.round_area(0.5*np.abs(np.dot(x, np.roll(y, 1))-np.dot(y, np.roll(x, 1))))

    def round_area(self, area):
        if area <= 0.03:
            return 3
        elif area <= 0.08:
            return 2
        else:
            return 1

    def build(self, n_points):
        points = np.array(
            sorted(self.generate_points(n_points), key=lambda x: x.sum()))
        reflected_points, points_center = self.reflect_points(points)
        vor = self.voronoi(reflected_points, points_center)
        tri = self.triangles(reflected_points, points_center)
        map_regions = []
        all_boundaries = []
        for idx, region in enumerate(vor.filtered_regions):
            boundaries = vor.vertices[region + [region[0]], :]
            all_boundaries += [
                boundary for boundary in boundaries.tolist() if boundary not in all_boundaries]
            centroid = self.centroid_region(boundaries)
            neighbours = set(
                [p+1 for simp in tri for p in simp if idx in simp if p != idx and p != -1])
            borders_map_edge = any([-1 in simp for simp in tri if idx in simp])
            region_area = self.polygon_area(boundaries)
            map_regions.append({"region_id": idx + 1,
                                "point": points[idx],
                                "centroid": centroid,
                                "random_point": points_in_polygon(boundaries.tolist()),
                                "boundaries": boundaries,
                                "neighbours": list(neighbours),
                                "borders_map_edge": borders_map_edge,
                                "area": region_area
                                })
        ridge_vertices = [vor.vertices[ridge]
                          for ridge in vor.ridge_vertices]
        filtered_ridges = [vertex for vertex in ridge_vertices if vertex[0].tolist(
        ) in all_boundaries and vertex[1].tolist() in all_boundaries]
        filtered_ridges = [{"vertices": edge.tolist(), "midpoint": ((edge[0]+edge[1])/2).tolist()}
                           for edge in filtered_ridges]

        midpoints = defaultdict(list)
        for ridge_info in filtered_ridges:
            for map_region in map_regions:
                if all([point in map_region["boundaries"] for point in ridge_info["vertices"]]):
                    midpoints[tuple(ridge_info["midpoint"])].append(
                        map_region["region_id"])
        midpoints = {tuple(sorted(v)): list(k) for k, v in midpoints.items()}
        return {"regions": sorted(map_regions, key=lambda x: x["region_id"]), "ridges": filtered_ridges, "midpoints": midpoints}


def points_in_polygon(vertices):
    points = []
    for idx in range(0, len(vertices), 2):
        weights = np.array([[1] for _ in range(len(vertices))])
        weights[idx] = [10]
        # weights[random.randint(0, len(weights)-1)] = [2]
        weights = weights/weights.sum() * len(vertices)
        weighted = vertices * weights
        points.append(weighted.mean(axis=0).tolist())
    return points
