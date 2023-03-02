import React from 'react';
import PropTypes from 'prop-types';

class Likes extends React.Component {
    constructor(props) {
        // Initialize mutable state
        super(props);
        this.state = { likeActive: false};
        
      }

    componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const  url  = this.props.likes_url;

    // Call REST API to get the post's information
    
  }

 
      
      // fetch(url_like, { credentials: 'same-origin' })
      // .then((response) => {
      //   if (!response.ok) throw Error(response.statusText);
      //   return response.json();
      // })
      // .then((data) => {
      //   this.setState({
      //     likes_count: data.likes_count,
      //   });
      // })
      // .catch((error) => console.log(error));
      
          
      
      render() {
        // This line automatically assigns this.state.imgUrl to the const variable imgUrl
        // and this.state.owner to the const variable owner
        
    
        // Render number of post image and post owner
        return ( 
          <div className="like"> 
          <button onClick={this.props.setLike}>{this.props.logname_likes_this}</button>
          
          <p>
          {this.props.likes_count}
          </p>
          </div>
          
        );
      }
}
export default Likes;