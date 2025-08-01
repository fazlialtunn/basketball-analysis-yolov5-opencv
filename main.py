import faulthandler
faulthandler.enable()
from utils import read_video, save_video
from trackers import PlayerTracker, BallTracker
from drawers import(
    PlayerTracksDrawer,
    BallTracksDrawer,
    TeamBallControlDrawer,
    PassAndInterceptionsDrawer,
    CourtKeypointsDrawer,
    TacticalViewDrawer,
    SpeedAndDistanceDrawer
)
from team_assigner import TeamAssigner
from ball_acquisition import BallAcquisitionDetector
from pass_and_interception_detector import PassAndInterceptionDetector
from court_keypoint_detector import CourtKeypointDetector
from tactical_view_converter import TacticalViewConverter
from speed_and_distance_calculator import SpeedAndDistanceCalculator
from configs import (
    PLAYER_DETECTOR_PATH,
    BALL_DETECTOR_PATH,
    COURT_KEYPOINT_DETECTOR_PATH,
    OUTPUT_VIDEO_PATH
)

def main():
    # read video
    video_frames = read_video("input_videos/video_1.mp4")

    # initialize tracker
    player_tracker = PlayerTracker(PLAYER_DETECTOR_PATH)
    ball_tracker = BallTracker(BALL_DETECTOR_PATH,)

    # run tracker
    player_tracks = player_tracker.get_object_tracks(video_frames, read_from_stub=True, stub_path="stubs/player_track_stubs.pkl")
    ball_tracks = ball_tracker.get_object_tracks(video_frames, read_from_stub=True, stub_path="stubs/ball_track_stubs.pkl")

    # get court keypoints
    court_keypoint_detector = CourtKeypointDetector(COURT_KEYPOINT_DETECTOR_PATH)
    court_keypoints = court_keypoint_detector.get_court_keypoints(video_frames, read_from_stub=True, stub_path="stubs/court_keypoint_stubs.pkl")

    # remove wrong ball detections
    ball_tracks = ball_tracker.remove_wrong_detections(ball_tracks)

    # interpolate missing ball detections
    ball_tracks = ball_tracker.interpolate_ball_positions(ball_tracks)

    # assign players to teams
    team_assigner = TeamAssigner()
    player_assignment = team_assigner.get_player_teams_across_frames(
        video_frames, player_tracks, read_from_stub=True, stub_path="stubs/player_team_stubs.pkl"
    )

    # ball acquisition detection
    ball_acquisition_detector = BallAcquisitionDetector()
    ball_acquisition = ball_acquisition_detector.detect_ball_possession(player_tracks, ball_tracks)

    # detect pass and interception
    pass_and_interception_detector = PassAndInterceptionDetector()
    passes = pass_and_interception_detector.detect_passes(ball_acquisition, player_assignment)
    interceptions = pass_and_interception_detector.detect_interceptions(ball_acquisition, player_assignment)

    # convert to tactical view
    tactical_view_converter = TacticalViewConverter(court_image_path="./images/basketball_court.png")
    court_keypoints = tactical_view_converter.validate_keypoints(court_keypoints)
    tactical_player_positions = tactical_view_converter.transform_players_to_tactical_view(court_keypoints, player_tracks)

    # speed and distance
    speed_and_distance_calculator = SpeedAndDistanceCalculator(
        tactical_view_converter.width,
        tactical_view_converter.height,
        tactical_view_converter.actual_width_in_meters,
        tactical_view_converter.actual_height_in_meters)
    player_distances_per_frame = speed_and_distance_calculator.calculate_distance(tactical_player_positions)
    player_speed_per_frame = speed_and_distance_calculator.calculate_speed(player_distances_per_frame)

    # initialize drawers
    player_tracks_drawer = PlayerTracksDrawer()
    ball_tracks_drawer = BallTracksDrawer()
    team_ball_control_drawer = TeamBallControlDrawer()
    pass_and_interceptions_drawer = PassAndInterceptionsDrawer()
    court_keypoints_drawer = CourtKeypointsDrawer()
    tactical_view_drawer = TacticalViewDrawer()
    speed_and_distance_drawer = SpeedAndDistanceDrawer()

    # draw objects
    output_video_frames = player_tracks_drawer.draw(video_frames, player_tracks, player_assignment, ball_acquisition)
    output_video_frames = ball_tracks_drawer.draw(output_video_frames, ball_tracks)

    # draw team ball control
    output_video_frames = team_ball_control_drawer.draw(output_video_frames, player_assignment, ball_acquisition)

    # draw passes and interceptions
    output_video_frames = pass_and_interceptions_drawer.draw(output_video_frames, passes, interceptions)

    # draw court keypoints
    output_video_frames = court_keypoints_drawer.draw(output_video_frames, court_keypoints)

    # tactical view
    output_video_frames = tactical_view_drawer.draw(output_video_frames,
                                                    tactical_view_converter.court_image_path,
                                                    tactical_view_converter.width,
                                                    tactical_view_converter.height,
                                                    tactical_view_converter.key_points,
                                                    tactical_player_positions,
                                                    player_assignment,
                                                    ball_acquisition
                                                    )
    
    # draw speed and distance
    output_video_frames = speed_and_distance_drawer.draw(output_video_frames,
                                                          player_tracks,
                                                          player_distances_per_frame,
                                                          player_speed_per_frame
                                                          )

    # save video    
    save_video(output_video_frames, OUTPUT_VIDEO_PATH)

if __name__ == "__main__":
    main()