import React from 'react';
import PropTypes from 'prop-types';

class Comments extends React.Component {
    constructor(props) {
        // Initialize mutable state
        super(props);
        this.state = { comment: ''};
        this.mapComment = this.mapComment.bind(this);
        
      }

componentDidMount() {
const comments_url = this.props.comments_url;

  }

      

      mapComment(){
        const comnt = this.state.comments.map((comment)  =>
    {comment});
        return (
          {comnt}
        )
      }

    
      render() {
        // const vals = this.state.comments;
        // console.log(vals);
        return (
          <div className="comment">
           {this.props.owner} <span> </span> {this.props.text} 
           
          </div>
        );
      }
}
export default Comments;