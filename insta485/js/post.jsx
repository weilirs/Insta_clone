import React from 'react';
import PropTypes from 'prop-types';
import Likes from './likes';
import Comments from './comments'
import moment from 'moment'

class Post extends React.Component {
  /* Display number of image and post owner of a single post
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { imgUrl: '', owner: '' , timestamp: '', owner_img_url: '', owner_show_url: '', likes_count: '', logname_likes_this: '', comments:[]};
    this.setLike = this.setLike.bind(this);
    this.doubleLike = this.doubleLike.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const  url  = this.props.url;
    const  likes_url = url+"likes/";
    const  comments_url = url+"comments/";

    // Call REST API to get the post's information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          imgUrl: data.img_url,
          owner: data.owner,
          timestamp: data.created,
          owner_img_url: data.owner_img_url,
          owner_show_url: data.owner_show_url,
        });
      })
      .catch((error) => console.log(error));

      fetch(likes_url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          likes_count: data.likes_count,
          logname_likes_this: data.logname_likes_this
        });
      })
      .catch((error) => console.log(error));

      fetch(comments_url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          comments:data.comments
        });
      })
      .catch((error) => console.log(error));
  }

  handleLikeClick(i) {
    const squares = this.state.squares.slice();
    if (calculateWinner(squares) || squares[i]) {
      return;
    }
    squares[i] = this.state.xIsNext ? 'X' : 'O';
    this.setState({
      squares: squares,
      xIsNext: !this.state.xIsNext,
    });
  }

  renderLikeClick(i) {
    return (
      <likes
        value={this.state.squares[i]}
        onClick={() => this.handleClick(i)}
      />
    );
  }

      setLike() {
       const url_like = this.props.url+"likes/";
       if(this.state.logname_likes_this == '1'){
         this.setState({logname_likes_this: 0});
         fetch(url_like, { method: 'DELETE' })
         this.setState({likes_count: this.state.likes_count-1});

       }
       else {
         this.setState({logname_likes_this: 1});
         fetch(url_like, { method: 'POST' })
         this.setState({likes_count: this.state.likes_count+1});
       }
    }

    doubleLike() {
      const url_like = this.props.url+"likes/";
      if(this.state.logname_likes_this == '0'){
        this.setState({logname_likes_this: 1});
         fetch(url_like, { method: 'POST' })
         this.setState({likes_count: this.state.likes_count+1});
      }
    } 

    

    handleChange(event) {
        this.setState({comment: event.target.value});
      }
    
      handleSubmit(event) {
        const url_comment = this.props.url+"comments/";
        var data = this.state.comment;
        console.log(data);
        fetch(url_comment, {
          method: 'POST', // or 'PUT'
          body: JSON.stringify(data), // data can be `string` or {object}!
          headers: new Headers({
            'Content-Type': 'application/json'
          })
        }).then(res => res.json())
        .catch(error => console.error('Error:', error))
        .then(response => {this.setState({comments: this.state.comments.concat(response)})});
        event.preventDefault();
      }
  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const { imgUrl, owner, timestamp, owner_img_url} = this.state;

    // Render number of post image and post owner
    return (
      <div className="post">
        <p>
        <a href="/u/{{owner}}/"><img src = {owner_img_url} alt="img1" width="100" height="100"/></a>
        <a href={this.props.url}>  {moment(timestamp, "YYYY-MM-DD hh:mm:ss").fromNow()} </a>
        </p>
        
        <img src={imgUrl} onDoubleClick={this.doubleLike}/>
        
        <p>
          {owner}

        </p>
        <Likes likes_url={this.props.like} setLike={this.setLike} likes_count={this.state.likes_count} logname_likes_this={this.state.logname_likes_this}/>
        {this.state.comments.map(comment => (<Comments commentid={comment.commentid} text={comment.text} owner={comment.owner} url_comment={this.props.url+"comments/"}/> ))}
        
          <form onSubmit={this.handleSubmit}>
        <label>
          Comment:
          <input type="text" value={this.state.comment} onChange={this.handleChange} />
        </label>
        <input type="submit" value="Submit" />
      </form>
        
      </div>
    );
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Post;